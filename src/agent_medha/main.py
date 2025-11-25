import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agent_medha.graph import create_graph

# Load environment variables
load_dotenv()

def main():
    print("Initializing agentMedha...")
    graph = create_graph()
    
    print("agentMedha is ready! (Type 'bye' to exit)")
    
    while True:
        try:
            user_input = input("User: ")
            if not user_input:
                continue
                
            initial_state = {"messages": [HumanMessage(content=user_input)]}
            
            # Stream the graph execution
            for event in graph.stream(initial_state):
                for key, value in event.items():
                    if "messages" in value:
                        last_msg = value["messages"][-1]
                        print(f"Agent: {last_msg.content}")
            
            if user_input.lower() == "bye":
                break
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
