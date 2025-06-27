"""
Azure OpenAI客户端
提供智能对话和自然语言处理功能
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AzureOpenAIClient:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if not self.endpoint or not self.api_key:
            print("⚠️  警告: Azure OpenAI配置未设置，AI功能将不可用")
            print("请在.env文件中设置AZURE_OPENAI_ENDPOINT和AZURE_OPENAI_API_KEY")
            self.available = False
        else:
            self.available = True
    
    def chat_completion(self, messages: list, max_tokens: int = 1000, temperature: float = 0.7) -> Optional[str]:
        """
        发送聊天完成请求到Azure OpenAI
        
        Args:
            messages: 消息列表
            max_tokens: 最大令牌数
            temperature: 温度参数
            
        Returns:
            AI回复内容或None
        """
        if not self.available:
            return "抱歉，AI功能暂时不可用。请配置Azure OpenAI设置。"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        data = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"❌ Azure OpenAI API错误: {response.status_code}")
                print(f"错误详情: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return None
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return None
    
    def analyze_booking_request(self, user_input: str) -> Dict[str, Any]:
        """
        分析用户的预订请求
        
        Args:
            user_input: 用户输入
            
        Returns:
            分析结果字典
        """
        if not self.available:
            return {"intent": "unknown", "entities": {}}
        
        system_message = """
        你是一个智能的机票预订助手。请分析用户的输入，识别意图和实体。
        
        可能的意图包括:
        - create_booking: 创建预订
        - search_booking: 查询预订
        - update_booking: 更新预订
        - cancel_booking: 取消预订
        - general_question: 一般问题
        
        请以JSON格式回复，包含:
        - intent: 意图
        - entities: 提取的实体（如姓名、航班号、日期等）
        - confidence: 置信度(0-1)
        - response: 建议的回复
        """
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]
        
        response = self.chat_completion(messages, max_tokens=500, temperature=0.3)
        
        try:
            # 尝试解析JSON响应
            if response and response.strip().startswith('{'):
                return json.loads(response)
            else:
                return {
                    "intent": "general_question",
                    "entities": {},
                    "confidence": 0.5,
                    "response": response or "我没有完全理解您的请求，请提供更多详细信息。"
                }
        except json.JSONDecodeError:
            return {
                "intent": "general_question", 
                "entities": {},
                "confidence": 0.3,
                "response": response or "抱歉，我遇到了一些技术问题。"
            }
    
    def generate_flight_recommendation(self, departure: str, arrival: str, flights: list) -> str:
        """
        生成航班推荐
        
        Args:
            departure: 出发地
            arrival: 目的地
            flights: 航班列表
            
        Returns:
            推荐文本
        """
        if not self.available:
            return f"找到 {len(flights)} 个从 {departure} 到 {arrival} 的航班。"
        
        flight_info = []
        for flight in flights:
            flight_info.append(f"航班 {flight.flight_number} ({flight.airline}) - 价格: ¥{flight.price}")
        
        system_message = f"""
        你是一个专业的航班推荐助手。请根据以下航班信息，为用户提供个性化的推荐建议。
        
        航线: {departure} → {arrival}
        可用航班:
        {chr(10).join(flight_info)}
        
        请提供简洁、实用的推荐建议，包括性价比分析和选择建议。
        """
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"请推荐从{departure}到{arrival}的航班"}
        ]
        
        response = self.chat_completion(messages, max_tokens=300, temperature=0.6)
        return response or f"为您找到 {len(flights)} 个航班选择，请根据时间和价格需求选择。"

# 创建全局客户端实例
azure_client = AzureOpenAIClient()
