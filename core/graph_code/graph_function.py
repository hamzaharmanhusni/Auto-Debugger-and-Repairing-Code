from typing import Dict, Optional, TypedDict
from langgraph.graph import END, StateGraph

from core.graph_code.data_model import Invoke

# import streamlit as st


class AgentCoder(TypedDict):
    requirement: str
    code: str 
    testing_code: str
    refactored_code:str
    tests: Dict[str, any]
    bug : Optional[str]
    errors: Optional[str]
    final_result: Optional[str]
    token_used: int
    prompt_token: int
    completion_token:int
    cost: float
    
class GraphProcess():
    def __init__(self, model, temperature):
        self.invoker = Invoke(model, temperature)
        
    def upload_code(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Upload Code------')
        code = state['code']
        print(f"Code : \n{code}")
        return{'code':code }

    def localizer(self, state):
        print('\n' + '----------' * 20)
        print('\n------Entering in Localizer------')
        requirement = state['requirement']
        code = state['code']
        localizer_response, localizer_info = self.invoker.localizer_invoke(requirement, code)
        print(localizer_info)
        print(f"Bug analyzed: {localizer_response.Description}")
        return {
            'bug': localizer_response.Description,
            'token_used': localizer_info.total_tokens,
            'prompt_token': localizer_info.prompt_tokens,
            'completion_token':  localizer_info.completion_tokens,
            'cost': localizer_info.total_cost
        }
                

    def executer(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Executer------')
        code = state['code']
        code_execute, execution_info = self.invoker.execution_invoke(code)
        code_to_execute = code+'\n\n'+code_execute.code
        print(f"Testing code : \n{code_execute.code}")
        print(execution_info)
        print(code_to_execute)
        error = None
        try:
            exec(code_to_execute)
            print("Code Execution Successful")
        except Exception as e:
            print('Found Error While Running')
            error = f"Execution Error : {e}"
        return {
            'testing_code':code_execute.code,
            'errors':error,
            'token_used': state['token_used'] + execution_info.total_tokens,
            'prompt_token': state['prompt_token'] + execution_info.prompt_tokens,
            'completion_token': state['completion_token'] + execution_info.completion_tokens,
            'cost': state['cost'] + execution_info.total_cost        
        }

    def debugger(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Debugger------')
        errors = state['errors']
        code = state['code']
        bug = state['bug']
        debug_code, debug_info = self.invoker.debug_code_invoke(code, bug, errors)
        print(debug_code)
        print(debug_info)
        return {
            'code':debug_code.code,
            'errors':None,
            'token_used': state['token_used'] + debug_info.total_tokens,
            'prompt_token': state['prompt_token'] + debug_info.prompt_tokens,
            'completion_token': state['completion_token'] + debug_info.completion_tokens,
            'cost': state['cost'] + debug_info.total_cost          
        }

    def decide_to_developer(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Decide to Developer------')
        if state['errors']:
            print(f'''There is error and bug. 
                    The error : {state["errors"]}
                    The bug : {state["bug"]}'''
                )
            return 'debugger'
        else:
            print("There is no error, the code will be refactored")
            return 'developer'

    def developer(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Decide to Developer------')
        code = state['code']
        refactored_code, refactored_code_info  = self.invoker.developer_invoke(code,lang="Python")
        code_to_execute = code + '\n' + refactored_code.code
        print(f"The refactored code : \n{refactored_code.code}")
        print(refactored_code_info)
        error = None
        try:
            exec(code_to_execute)
            print("Developer Code Execution Successful")
        except Exception as e:
            print('Found Error While Running')
            error = f"Execution Error : {e}"
        return {
            'refactored_code':refactored_code.code,
            'errors':error,
            'token_used': state['token_used'] + refactored_code_info.total_tokens,
            'prompt_token': state['prompt_token'] + refactored_code_info.prompt_tokens,
            'completion_token': state['completion_token'] + refactored_code_info.completion_tokens,
            'cost': state['cost'] + refactored_code_info.total_cost    
        }
        
    def decide_to_end(self, state):
        print('\n'+'----------'*20)
        print(f'\n------Entering in Decide to End------')
        if state['errors']:
            print("This code error when refactored, it will be return the debugger code")
            return 'the_end'
        else:
            print("----The code can be refactored----")
            return 'end'
        
    def the_end(self, state):
        print('\n'+'----------'*20)
        code = state["code"]
        return {"code":code,"final_result":"Can not use code refactor"}