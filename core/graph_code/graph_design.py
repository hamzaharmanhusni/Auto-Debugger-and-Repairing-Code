from langgraph.graph import END, StateGraph
from core.graph_code.graph_function import (
    AgentCoder,
    GraphProcess
)
from IPython.display import Image
import os
from dotenv import load_dotenv
        

def design_graph_code(api_key, model, temperature):
    
    if api_key:
        os.environ['OPENAI_API_KEY']=api_key
    else:
        load_dotenv()
    graph_process = GraphProcess(model = model, temperature = temperature)
    workflow = StateGraph(AgentCoder)
    
    # Define the nodes
    workflow.add_node("upload_code",graph_process.upload_code)
    workflow.add_node("localizer", graph_process.localizer)  
    workflow.add_node("executer", graph_process.executer) 
    workflow.add_node("debugger", graph_process.debugger) 
    workflow.add_node("developer",graph_process.developer )
    workflow.add_node("the_end",graph_process.the_end)

    # Build graph
    workflow.set_entry_point("upload_code")
    workflow.add_edge("upload_code", "localizer")
    workflow.add_edge("localizer","executer")
    workflow.add_edge("debugger", "executer")
    # workflow.add_edge("developer", "decide_to_end")
    workflow.add_edge("the_end",END)
    #workflow.add_edge("executer", "decide_to_end")

    workflow.add_conditional_edges(
        'executer',
        graph_process.decide_to_developer,
        {
            "debugger": "debugger",
            "developer": "developer"    
        }
    )

    workflow.add_conditional_edges(
        "developer",
        graph_process.decide_to_end,
        {
            "end" : END,
            'the_end':'the_end'
        }    
    )

    # Compile
    app = workflow.compile()
    # flowchart =Image(app.get_graph().draw_png())
    return app

    