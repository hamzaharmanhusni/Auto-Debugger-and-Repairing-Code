from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import create_structured_output_runnable
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional
from langchain_community.callbacks import get_openai_callback


class Localizer(BaseModel):
    Description: str = Field(
        description="The bug from the code : "
    )

class ExecutableCode(BaseModel):
    code: str = Field(
        description="Detailed optmized error-free Python code with test cases assertion"
    )

class DebugCode(BaseModel):
    code: str = Field(
        description="Optimized and Refined Python code to resolve the error"
    ) 

class RefactorCode(BaseModel):
    code: str = Field(
        description="Refactored Python code "
    )
    
    
class Invoke():
    def __init__(self, model, temperature):
        # self.client=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.2)
        self.client=ChatOpenAI(model=model, temperature=temperature)

    def localizer_invoke(self, requirement, code):    
        localization_gen_prompt = ChatPromptTemplate.from_template(
            '''**Role**: As a debugger, your task is to identify any issues in the provided code. If no issues are found, simply state that the code is bug-free. If there are issues, explain them clearly.
        {requirement}
        **Code**
        {code}
        '''
        )
        localizer_agent = create_structured_output_runnable(
            Localizer, self.client, localization_gen_prompt
        )
        with get_openai_callback() as localizer_info:
            localizer_invoke=localizer_agent.invoke({'code':code,'requirement':requirement})
        return localizer_invoke, localizer_info

    def execution_invoke(self, code):
        code = code
        python_execution_gen = ChatPromptTemplate.from_template(
            """You just make a testing layer in the *Python Code* that can help to execute the code. You need to pass only Input as argument and validate if the Given Output is matched.
        *Instruction*:
        - Make sure to return the error if the assertion fails
        - Generate the code that can be execute, make sure it has `if __name__ == '__main__': ` in the beginning so that it is executable
        Python Code to execute:
        
        *Python Code*:{code}

        Input and Output For Code:
        *Input*: generate input to test
        *Expected Output*:generate output expected from input

        You just state the test layer, such as :
        
        if __name__ == '__main__:
            assert method(Input1) == 'Expected Output1', 'The description why error happen'
            assert method(Input2) == 'Expected Output2', 'The description why error happen'
        
        Make sure the output just test layer without given code.
        """
        )
        execution_agent = create_structured_output_runnable(
            ExecutableCode, self.client, python_execution_gen
        )  
        with get_openai_callback() as execution_info:
            execution_invoke= execution_agent.invoke({"code":code})
        return execution_invoke,execution_info

    def debug_code_invoke(self, code, bug, errors=None):
        python_debug_gen = ChatPromptTemplate.from_template(
            """You are expert in Python Debugging. You have to analysis Given Code and Bug and generate code that handles the Bug
            *Instructions*:
            - Make sure to generate error free code
            - Generated code is able to handle the bug
            
            *Code*: {code}
            *Bug analyzed*:  {bug}
            *Error detected*: {error}
            """
        )
        debug_code_agent = create_structured_output_runnable(
            DebugCode, self.client, python_debug_gen
        )
        with get_openai_callback() as debug_info:
            debug_code_invoke=debug_code_agent.invoke({'code':code,'bug':bug,'error':errors})   
        
        return debug_code_invoke,debug_info

    def developer_invoke(self, code : str, lang:str):
        python_refactored_code = ChatPromptTemplate.from_template("""Your task as an expert developer,  you are given the code that needs to be refactored and optimized for better performance, readability, and maintainability. Below are the details and the code snippet. Please refactor the code, provide comments where necessary, and suggest any improvements or best practices that can be applied.

        Details:

        - The code should follow {lang} best practices.
        - Aim for improved performance without sacrificing readability.
        - Ensure that the code is modular and easy to maintain.
        - Add comments to explain complex sections of the code.
        - Optimize any redundant or inefficient parts of the code.
        - Ensure proper error handling and input validation.
        - Follow naming conventions for variables and functions.

        Code Snippet:
        {code}

        Please provide the refactored and optimized version of the code along with any comment of explanations or suggestions for improvements."""
        )
        refactor_code_agent = create_structured_output_runnable(
            RefactorCode, self.client, python_refactored_code
        )
        with get_openai_callback() as refactor_code_info:
            refactor_code_invoke=refactor_code_agent.invoke({"lang":lang,"code":code})
        return refactor_code_invoke,refactor_code_info