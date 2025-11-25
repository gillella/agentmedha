import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

from agent_medha.graph import create_graph
from langchain_core.messages import HumanMessage

load_dotenv()

# Force removal of ADC if present to avoid conflicts
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

# Initialize Graph
graph = create_graph()

# Test Data
questions = [
    "What is my name?",
    "What is my favorite color?",
    "Where do I live?"
]

ground_truths = [
    ["Aravind"],
    ["Purple"],
    ["New York"]
]

def generate_responses():
    contexts = []
    answers = []
    
    for q in questions[:1]: # Run only 1 question for debug
        print(f"Processing: {q}")
        try:
            # Use sync invoke
            state = graph.invoke({"messages": [HumanMessage(content=q)]})
            
            # Extract answer
            last_msg = state["messages"][-1]
            answers.append(last_msg.content)
            
            # Extract context (if available in state, otherwise empty)
            # Note: Our graph stores context in state["context"]
            ctx_docs = state.get("context", [])
            contexts.append([doc.page_content for doc in ctx_docs])
            print(f"Answer: {last_msg.content}")
        except Exception as e:
            print(f"Error processing {q}: {e}")
            import traceback
            traceback.print_exc()
        
    return answers, contexts

def run_eval():
    print("Generating responses...")
    # Run sync
    answers, contexts = generate_responses()
    
    # Filter data to match what was processed
    processed_count = len(answers)
    if processed_count == 0:
        print("No answers generated. Exiting.")
        return

    data = {
        "question": questions[:processed_count],
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths[:processed_count]
    }
    
    dataset = Dataset.from_dict(data)
    
    print("Running RAGAS evaluation...")
    # Configure RAGAS to use Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=os.getenv("GEMINI_API_KEY"))
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=os.getenv("GEMINI_API_KEY"))
    
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
        ],
        llm=llm,
        embeddings=embeddings
    )
    
    print("\nEvaluation Results:")
    print(results)
    
    # Save results
    df = results.to_pandas()
    df.to_csv("eval_results.csv", index=False)
    print("Results saved to eval_results.csv")

if __name__ == "__main__":
    run_eval()
