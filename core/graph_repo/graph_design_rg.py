from langgraph.graph import END, StateGraph
from core.graph_repo.graph_function_rg import (
    AgentCoder,
    GraphProcess
    # upload_code,
    # localizer,
    # explanation,
    # repairer,
    # crafter,
    # developer
)
from IPython.display import Image
import os
from dotenv import load_dotenv
        

def design_graph_path(api_key, model, temperature):
    
    if api_key:
        os.environ['OPENAI_API_KEY']=api_key
    else:
        load_dotenv()
        
    graph_process = GraphProcess(model = model, temperature = temperature)
    workflow = StateGraph(AgentCoder)
    
    # Define the nodes
    workflow.add_node("upload_code",graph_process.upload_code)
    workflow.add_node("localizer", graph_process.localizer)  
    workflow.add_node("explanation", graph_process.explanation) 
    workflow.add_node("repairer", graph_process.repairer) 
    workflow.add_node("crafter", graph_process.crafter)
    workflow.add_node("developer",graph_process.developer )

    # Build graph
    workflow.set_entry_point("upload_code")
    workflow.add_edge("upload_code", "localizer")
    workflow.add_edge("localizer","explanation")
    workflow.add_edge("explanation", "repairer")
    workflow.add_edge("repairer", "crafter")
    workflow.add_edge("crafter", "developer")
    workflow.add_edge("developer",END)
    # Compile
    app = workflow.compile()
    # flowchart =Image(app.get_graph().draw_png())
    return app