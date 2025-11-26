from dotenv import load_dotenv
from agent_medha.memory_manager import MemoryManager

load_dotenv()

def populate_memory():
    print("Populating agent_medha_memory...")
    mm = MemoryManager() # Uses default 'agent_medha_memory'
    
    # Clear existing to be safe
    # mm.clear_memory() 
    
    # Add facts
    mm.add_memory("My name is Aravind.", memory_type="semantic", agent_id="global")
    mm.add_memory("My favorite color is Purple.", memory_type="semantic", agent_id="global")
    mm.add_memory("I live in New York.", memory_type="semantic", agent_id="global")
    
    print("Memory populated.")

if __name__ == "__main__":
    populate_memory()
