
import asyncio
from swarms import Agent
from swarms.tools.mcp_integration import MCPServerSseParams
import logging

class MathAgent:
    def __init__(self, name: str, server_url: str):
        self.server = MCPServerSseParams(
            url=server_url,
            headers={"Content-Type": "application/json"}
        )
        
        self.agent = Agent(
            agent_name=name,
            agent_description=f"{'Calculator' if name == 'Calculator' else 'Stock Analyst'} agent specializing in {'mathematical calculations' if name == 'Calculator' else 'stock market analysis'}. For Calculator: use add, multiply, divide operations. For Stock Analyst: use moving averages and percentage change calculations.",
            system_prompt=f"You are {name}, a math processing agent. You have access to these mathematical operations ONLY: addition, multiplication, and division. Only suggest calculations using these available tools. Do not attempt to solve problems requiring other operations like percentages, square roots, or advanced math. When users ask about capabilities, list only the basic operations you can perform.",
            max_loops=1,
            mcp_servers=[self.server],
            streaming_on=False,
            model_name="gpt-4o-mini",
            temperature=0.1,
            max_tokens=1000
        )

    async def process(self, task: str):
        try:
            # Check if asking about capabilities
            if any(word in task.lower() for word in ['what', 'how', 'can', 'capabilities', 'help']):
                if self.agent.agent_name == "Calculator":
                    return {
                        "agent": self.agent.agent_name,
                        "task": task,
                        "response": "I can perform basic mathematical operations: addition (use '+' or 'plus'), multiplication (use '*' or 'times'), and division (use '/' or 'divide by'). For example: '5 plus 3' or '10 divide by 2'"
                    }
                else:  # StockAnalyst
                    return {
                        "agent": self.agent.agent_name,
                        "task": task,
                        "response": "I can analyze stock data using moving averages and calculate percentage changes. For example: 'calculate moving average of [10,20,30,40,50] over 3 periods'"
                    }
            
            # Check if input is stock-related (for StockAnalyst)
            if self.agent.agent_name == "StockAnalyst" and "moving average" in task.lower():
                try:
                    import re
                    # Extract list of numbers and period
                    numbers = re.findall(r'\[([\d,\s]+)\]', task)
                    period = re.findall(r'over\s+(\d+)\s+periods', task)
                    
                    if numbers and period:
                        numbers = [float(n) for n in numbers[0].split(',')]
                        period = int(period[0])
                        if len(numbers) >= period:
                            # Calculate moving average
                            averages = []
                            for i in range(len(numbers) - period + 1):
                                avg = sum(numbers[i:i+period]) / period
                                averages.append(round(avg, 2))
                            return {
                                "agent": self.agent.agent_name,
                                "task": task,
                                "response": f"Moving averages: {averages}"
                            }
                except Exception as e:
                    return {
                        "agent": self.agent.agent_name,
                        "task": task,
                        "error": f"Error calculating moving average: {str(e)}"
                    }
            
            # Check if input is math-related (for Calculator)
            if self.agent.agent_name == "Calculator":
                math_keywords = ['add', 'plus', '+', 'multiply', 'times', '*', 'x', 'divide', '/', 'by']
                if not any(keyword in task.lower() for keyword in math_keywords):
                    return {
                        "agent": self.agent.agent_name,
                        "task": task,
                        "response": "Please provide a mathematical operation (add, multiply, or divide)"
                    }
            
            response = await self.agent.arun(task)
            return {
                "agent": self.agent.agent_name,
                "task": task,
                "response": str(response)
            }
        except Exception as e:
            logging.error(f"Error in {self.agent.agent_name}: {str(e)}")
            return {
                "agent": self.agent.agent_name,
                "task": task,
                "error": str(e)
            }

class MultiAgentMathSystem:
    def __init__(self):
        math_url = "http://0.0.0.0:8000"
        stock_url = "http://0.0.0.0:8001"
        self.calculator = MathAgent("Calculator", math_url)
        self.stock_analyst = MathAgent("StockAnalyst", stock_url)

    async def process_task(self, task: str):
        # Process with both agents
        results = await asyncio.gather(
            self.calculator.process(task),
            self.stock_analyst.process(task)
        )
        return results

    def run_interactive(self):
        print("\nMulti-Agent Math System")
        print("Enter 'exit' to quit")
        
        while True:
            try:
                user_input = input("\nEnter a math problem: ")
                if user_input.lower() == 'exit':
                    break

                results = asyncio.run(self.process_task(user_input))
                
                print("\nResults:")
                for result in results:
                    if "error" in result:
                        print(f"\n{result['agent']} encountered an error: {result['error']}")
                    else:
                        print(f"\n{result['agent']}: {result['response']}")

            except Exception as e:
                print(f"System error: {str(e)}")

if __name__ == "__main__":
    system = MultiAgentMathSystem()
    system.run_interactive()
