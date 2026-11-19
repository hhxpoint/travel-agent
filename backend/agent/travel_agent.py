"""
旅游攻略智能体 - LangChain Agent核心模块
基于LangChain框架构建的旅游攻略智能体
支持工具调用、对话记忆、RAG检索增强
"""

import os
import sys
from typing import List, Dict, Optional, Any
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ========== 修复导入：使用 langgraph 的新 Agent API ==========
from langgraph.prebuilt import create_react_agent

# 添加项目根目录
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent.tools import TOOLS
from agent.prompts import SYSTEM_PROMPT, WELCOME_MESSAGE, get_chat_history_prompt
import config


class TravelAgent:
    """旅游攻略智能体"""

    def __init__(self):
        """初始化智能体"""
        self.llm = self._init_llm()
        self.tools = TOOLS
        self.agent_executor = self._build_agent()   # 兼容旧属性名
        self.chat_history: List[Dict] = []

    def _init_llm(self) -> ChatOpenAI:
        """初始化大模型"""
        return ChatOpenAI(
            model=config.LLM_MODEL,
            openai_api_key=config.LLM_API_KEY,
            openai_api_base=config.LLM_BASE_URL,
            temperature=0.7,
            max_tokens=2000,
        )

    def _build_agent(self) -> Any:
        """
        构建 LangGraph Agent 并包装为兼容旧接口的调用对象
        返回的对象具有 .invoke() 方法，接受 {"input": ..., "chat_history": ...}
        返回格式兼容原有 AgentExecutor 的输出结构
        """
        # 使用 create_react_agent 替代旧的 AgentExecutor
        graph_agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            state_modifier=SYSTEM_PROMPT   # 系统提示词
        )

        # 定义包装器，让调用方式与旧的 AgentExecutor 兼容
        class CompatibleAgentWrapper:
            def __init__(self, graph_agent, tools):
                self.graph_agent = graph_agent
                self.tools = tools

            def invoke(self, inputs: Dict) -> Dict:
                """
                输入: {"input": str, "chat_history": List[BaseMessage]}
                输出: {"output": str, "intermediate_steps": List[Tuple[AgentAction, str]]}
                """
                user_input = inputs["input"]
                chat_history = inputs.get("chat_history", [])

                # 构建 LangGraph 所需的消息格式
                messages = []
                for msg in chat_history:
                    if isinstance(msg, HumanMessage):
                        messages.append(("user", msg.content))
                    elif isinstance(msg, AIMessage):
                        messages.append(("assistant", msg.content))
                messages.append(("user", user_input))

                # 调用图 agent
                result = self.graph_agent.invoke({"messages": messages})

                # 从结果中提取最终回复
                all_messages = result["messages"]
                final_output = ""
                intermediate_steps = []

                for m in reversed(all_messages):
                    if hasattr(m, "type") and m.type == "ai" and not final_output:
                        final_output = m.content
                    if hasattr(m, "tool_calls") and m.tool_calls:
                        for tc in m.tool_calls:
                            intermediate_steps.append((tc, None))

                if not final_output:
                    final_output = "抱歉，我无法生成回答，请稍后再试。"

                return {
                    "output": final_output,
                    "intermediate_steps": intermediate_steps
                }

        return CompatibleAgentWrapper(graph_agent, self.tools)

    def chat(self, user_input: str) -> Dict:
        """处理用户输入并返回回复"""
        try:
            history_messages = []
            for msg in self.chat_history[-10:]:
                if msg["role"] == "user":
                    history_messages.append(HumanMessage(content=msg["content"]))
                else:
                    history_messages.append(AIMessage(content=msg["content"]))

            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": history_messages,
            })

            output = result.get("output", "抱歉，我无法处理您的请求。")

            tool_calls = []
            for step in result.get("intermediate_steps", []):
                if isinstance(step, tuple) and len(step) >= 1:
                    tc = step[0]
                    tool_name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                    tool_input = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", None)
                    if tool_name:
                        tool_calls.append({
                            "tool": tool_name,
                            "input": tool_input,
                        })

            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": output})

            return {
                "success": True,
                "response": output,
                "tool_calls": tool_calls,
            }

        except Exception as e:
            error_msg = f"处理请求时出错: {str(e)}"
            return {
                "success": False,
                "response": error_msg,
                "tool_calls": [],
            }

    def clear_history(self):
        """清空聊天历史"""
        self.chat_history = []

    def get_welcome(self) -> str:
        """获取欢迎消息"""
        return WELCOME_MESSAGE


class SimpleTravelAgent:
    """
    简化版智能体 - 不依赖LangChain Agent
    直接使用LLM + 工具调用的简单实现
    用于在LangChain Agent出现问题时的备选方案
    """

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
        )
        self.chat_history: List[Dict] = []
        self.tools = self._build_tools_schema()

    def _build_tools_schema(self) -> List[Dict]:
        """构建OpenAI格式的工具schema"""
        from agent.tools import TOOLS
        schemas = []
        for tool in TOOLS:
            schema = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.args_schema.schema() if hasattr(tool, 'args_schema') and tool.args_schema else {"type": "object", "properties": {}},
                }
            }
            schemas.append(schema)
        return schemas

    def chat(self, user_input: str) -> Dict:
        """处理用户输入"""
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            for msg in self.chat_history[-10:]:
                messages.append(msg)

            messages.append({"role": "user", "content": user_input})

            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=2000,
            )

            msg = response.choices[0].message
            tool_calls_info = []

            if msg.tool_calls:
                messages.append(msg.model_dump())

                for tc in msg.tool_calls:
                    tool_result = self._execute_tool(tc.function.name, tc.function.arguments)
                    tool_calls_info.append({
                        "tool": tc.function.name,
                        "input": tc.function.arguments,
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_result,
                    })

                response = self.client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,
                )
                msg = response.choices[0].message

            output = msg.content or "抱歉，我无法处理您的请求。"

            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": output})

            return {
                "success": True,
                "response": output,
                "tool_calls": tool_calls_info,
            }

        except Exception as e:
            return {
                "success": False,
                "response": f"处理请求时出错: {str(e)}",
                "tool_calls": [],
            }

    def _execute_tool(self, tool_name: str, arguments: str) -> str:
        """执行工具调用"""
        import json
        from agent.tools import TOOLS

        args = json.loads(arguments) if isinstance(arguments, str) else arguments

        for tool in TOOLS:
            if tool.name == tool_name:
                try:
                    return tool.invoke(args)
                except Exception as e:
                    return f"工具执行出错: {str(e)}"

        return f"未找到工具: {tool_name}"

    def clear_history(self):
        self.chat_history = []

    def get_welcome(self) -> str:
        return WELCOME_MESSAGE