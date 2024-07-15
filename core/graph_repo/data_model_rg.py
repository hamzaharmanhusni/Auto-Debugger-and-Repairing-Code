from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.openai_functions import create_structured_output_runnable
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional
from langchain_community.callbacks import get_openai_callback


class Localizer(BaseModel):
    predicted_bug: str = Field(
        description="A description of the predicted bug in the code."
    )

class Explanation(BaseModel):
    function_explanation: str = Field(
        description="The explanation of the code."
    )

class Repairer(BaseModel):
    repair_description: str = Field(
        description="A description of the code that needs to be repaired."
    )

class Crafter(BaseModel):
    improved_code: str = Field(
        description="The python code after repairing."
    )

class Developer(BaseModel):
    refactored_code: str = Field(
        description="The refactored and optimized Python code."
    )

    
class Invoke():
    def __init__(self, model, temperature):
        # self.client=ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.client=ChatOpenAI(model=model, temperature=temperature)
        # self.client = client

    def localizer_invoke(self, requirement, code):    
        localization_gen_prompt = ChatPromptTemplate.from_template(
        '''
        **Role**: As a localizer, your task is to review the following code snippet and identify any potential bugs. Ignore any issues related to missing dependencies or packages. Focus on syntax errors, logical errors, and potential runtime issues within the given code. Provide a detailed explanation of each identified bug and suggest possible fixes. If no issues are found, simply state that the code is bug-free. If there are issues, explain them clearly.

        **Requirement**:
        {requirement}

        **Provided resources**:
        {code}

        The first row is counted after **Code**
        
        So it is like : 
        Source : path/to/file
        
        **Code** : 
        Row 1
        Row 2
        Row 3 
        And so on
        
        Your output must be in the following format:

        **predicted 1**:
        Predicted error code 1 -- source : path/to/file -- Row -- Explanation of the error and why it occurs\n\n
        **predicted 2**:
        Predicted error code 2 -- source : path/to/file -- Row -- Explanation of the error and why it occurs\n\n
        Cantinue this pattern for all predicted code

        Please review the code accordingly.
        '''    
        )
        localizer_agent = create_structured_output_runnable(
            Localizer, self.client, localization_gen_prompt
        ) 
        with get_openai_callback() as localizer_info:
            localizer_invoke = localizer_agent.invoke({'code':code,'requirement':requirement})
        return localizer_invoke, localizer_info
    
    def explanation_invoke(self, code):
        expalanation_gen_prompt = ChatPromptTemplate.from_template(
        """ 
        **Role** : As an identifier, you will provide an explanation of the code given. Then, You should specify the workflow or processing steps within the code. 
        
        **Given code** : 
        {code}
        
        Analyze the code to identify the function and process on the code.
        
        Follow this structured format:

        1. **Name of Class 1**: Provide a summarized overview of Class 1.
            - a) **Name of Method or Async Method 1 of the Class 1**: Describe the function and purpose of Method 1.
            - b) **Name of Method Async Method 2 of the Class 1**: Describe the function and purpose of Method 2.
            - Continue this pattern for all methods in Class 1.
        2. **Name of Class 2**: Provide a summarized overview of Class 2.
            - a) **Name of Method or Async Method 1 of the Class 2**: Describe the function and purpose of Method 1.
            - b) **Name of Method or Async Method 2 of the Class 2**: Describe the function and purpose of Method 2.
            - Continue this pattern for all methods in Class 2.
            
        - Continue this pattern for all remaining classes.

        After detailing the functions of each class and method, provide an overall explanation of the code's workflow. 

        Explain the process of the given code, predicting the overall function. If the code involves any dependencies or packages that are not explicitly stated, please predict their function as well.
        """    
        )
        
        explanation_agent = create_structured_output_runnable(
            Explanation, self.client, expalanation_gen_prompt
        )
        with get_openai_callback() as explanation_info:
            explanation_invoke = explanation_agent.invoke({'code':code})
        return explanation_invoke, explanation_info

    def repairer_invoke(self, code, bug, explanation):        
        repairer_gen_prompt = ChatPromptTemplate.from_template(
        """
        **Role** : As a code repairer, your task is to provide the corrected version based on any predicted bugs and the explanation of the code. 

        You will be given the predicted bug(s). 
        
        **Code** : 
        {code}
        
        **The explanation of the code**
        {explanation}
        
        **Predicted bug** 
        {bug}

        For each bug, follow this format:
        ---------------------------------------------------------------------------------------------\n
        **Error 1**:
        ```Write the code with error 1``` \n -- specify the row(s)\n  
        **After repair 1**:
        ```the code after repairing error 1```  
        **Explanation**: Explain what you have repaired.
        \n\n
        ---------------------------------------------------------------------------------------------\n
        **Error 2**:
        ```Write the code with error 2``` \n -- specify the row(s)\n  
        **After repair 2**:
        ```the code after repairing error 2```  
        **Explanation**: Explain what you have repaired.
        \n\n
        Continue this pattern for any additional errors.

        """
        )
        repairer_agent = create_structured_output_runnable(
            Repairer, self.client, repairer_gen_prompt
        )  
        with get_openai_callback() as repairer_info:
            repairer_invoke= repairer_agent.invoke({"code":code,"bug":bug, "explanation":explanation})
        return repairer_invoke, repairer_info

    def crafter_invoke(self, code, repair_description):
        repair_description = repair_description
        crafter_gen_prompt = ChatPromptTemplate.from_template(
        """
        **Role** : As a crafter, your task is to review the provided code.If there are no bugs, simply return the given code. If you are given any repaired description, repair them and merge the corrected code into the original. The output should be string.
        
        The original source : 
        {code}
        
        The first row is counted after **Code**
        
        So it is like : 
        Source : path/to/file
        
        **Code** : 
        Row 1
        Row 2
        Row 3 
        And so on

        **The description of the code that should be repaired:**
        {repair_description}
        
        **If the code is bug-free.** : 
        Just state the code that is given
        
        Instructions if the code should be repaired:

        1. Examine the changes and improvements detailed in the "The description of the code that should be repaired" section.
        2. Carefully integrate the corrections into the original code, ensuring all improvements and corrections are included.
        3. Provide the complete, corrected code as the final output.
        4. Ensure the code is error-free, disregarding issues related to missing dependencies or packages.
        """
        )
        crafter_agent = create_structured_output_runnable(
            Crafter, self.client, crafter_gen_prompt
        )
        with get_openai_callback() as crafter_info:
            crafter_invoke=crafter_agent.invoke({'code':code,'repair_description':repair_description})   
        
        return crafter_invoke,crafter_info

    def developer_invoke(self, code : str, lang:str):
        developer_gen_prompt = ChatPromptTemplate.from_template(
        """
        Your task as an expert developer,  you are given the code that needs to be refactored and optimized for better performance, readability, and maintainability. Below are the details and the code snippet. Please refactor the code, provide comments where necessary, and suggest any improvements or best practices that can be applied.

        Details:

        - The code should follow {lang} best practices.
        - Ignoring the missing depedencies or packages
        - Aim for improved performance without sacrificing readability.
        - Ensure that the code is modular and easy to maintain.
        - Add comments to explain complex sections of the code.
        - Optimize any redundant or inefficient parts of the code.
        - Follow naming conventions for variables and functions.

        Code Snippet:
        {code}

        Please provide the refactored and optimized version of the code along with any comment of explanations or suggestions for improvements."""
        )
        developer_agent = create_structured_output_runnable(
            Developer, self.client, developer_gen_prompt
        )
        with get_openai_callback() as developer_info:
            developer_invoke=developer_agent.invoke({"lang":lang,"code":code})
        return developer_invoke,developer_info