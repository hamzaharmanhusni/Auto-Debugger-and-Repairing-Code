import streamlit as st
from interface.sidebar import sidebar
from openai import OpenAI
from streamlit.logger import get_logger
import asyncio
from core.graph_code.graph_design import design_graph_code
from core.graph_repo.graph_design_rg import design_graph_path
logger = get_logger(__name__)


@st.cache_data(show_spinner=False)
def is_open_ai_key_valid(openai_api_key, model: str) -> bool:
    if not openai_api_key:
        st.error("Please enter your OpenAI API key in the sidebar!")
        return False
    
    try:
        client=OpenAI(api_key=openai_api_key)
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "test"}]
        )
    except Exception as e:
        st.error(f"{e.__class__.__name__}: {e}")
        logger.error(f"{e.__class__.__name__}: {e}")
        return False

    return True

async def run_code(api_key, code, requirement, limit, running_dict, path, model, temperature):
    config = {"recursion_limit": limit}
    inputs = {
        "requirement": requirement,
        "code": code
    }
    counter = 0
    recursion_limit = limit
    if path == "code" :
        app = design_graph_code(api_key, model, temperature)
    else:
        app = design_graph_path(api_key, model, temperature)
    
    # async for event in app.astream(inputs, config=config):
        # for k, v in event.items():
        # if counter >= recursion_limit:
        #     st.error("Recursion limit exceeded.")
        #     raise RecursionError("Recursion limit exceeded.")
        # running_dict[k] = v
        # if k != "__end__":
        #     st.write(v)
        #     st.write('----------' * 20 + '\n')
        #     await asyncio.sleep(0.1)  # Ensure Streamlit can process updates
        # counter += 1
    try:
        async for event in app.astream(inputs, config=config):
            for k, v in event.items():
                if counter >= recursion_limit:
                    st.error("Recursion limit exceeded.")
                    raise RecursionError("Recursion limit exceeded.")
                
                running_dict[k] = v
                if k != "__end__":
                    st.write(v)
                    st.write('----------' * 20 + '\n')
                    await asyncio.sleep(0.1)  # Ensure Streamlit can process updates
                counter += 1
    except RecursionError as e:
        st.error(str(e))


async def main():
    st.set_page_config(page_title="Auto Debugger and Repairing Code", page_icon="💻", layout="wide")
    st.header("👨‍💻Auto Debugger👨‍💻")

    sidebar()
    openai_api_key = st.session_state.get("OPENAI_API_KEY")

    MODEL_LIST = ["gpt-3.5-turbo", "gpt-4o"]

    if not openai_api_key:
        st.warning(
            "Enter your OpenAI API key in the sidebar. You can get a key at"
            " https://platform.openai.com/account/api-keys."
        )    
    
    model: str = st.selectbox("Model", options=MODEL_LIST)  # type: ignore
    temperature: int = st.number_input("Temperature", value=0.2)
    
    if not is_open_ai_key_valid(openai_api_key, model):
        st.stop() 
    
    # chunked_fiel = 
    
    # chunk_button = st.button("Chunk Process")
    
    # if chunk_button:
    #     chunks = chunk_file(path_file, chunk_size=200, chunk_overlap=0)
    #     st.write(chunks)
    
    st.subheader("Detect bug and repairing from Path")
    limit = st.number_input("Recursion Limit", value=10)
    requirement = st.text_input("Requirement", "some_requirement")
    process_type: str = st.selectbox("Process :", options=["Process Path", "Process the code"])
    
    if process_type == "Process Path":
        st.subheader("Input Path")    
        uploaded_file = st.file_uploader(
            "Upload your code",
            type=["py", "java", "go", "txt"],
            help="Scanned documents are not supported yet!",
        )

        if not uploaded_file:
            st.stop()

        process = st.button("Process path")

        if process:
            try:
                with uploaded_file:
                    code = uploaded_file.read().decode('utf-8')
                    file_name = uploaded_file.name
            except AttributeError:
                st.error("File not uploaded or invalid file type selected.")
            except UnicodeDecodeError:
                st.error("Unable to decode the file as UTF-8.")
            code = f"Sources: {file_name}\n\n**Code**:\n```python\n{code}\n```"
                # st.markdown(code)
            
            running_dict = {}
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["All", "Code", "Localizer", "Explanation", "Repairer", "Crafter", "Developer", "Price Analysis"])
            
            with tab1:
                path="file_path"
                await run_code(openai_api_key, code, requirement, limit, running_dict, path, model, temperature)
            with tab2:
                if "upload_code" in running_dict:
                    st.markdown(f"**Code uploaded** : \n\n\n{running_dict['upload_code']['code']}")
                else:
                    st.write("No code detected")
            with tab3:
                if "localizer" in running_dict:
                    st.markdown(f"**Bug Detected** : \n\n{running_dict['localizer']['predicted_bug']}")
                else:
                    st.write("No localizer data available")
            with tab4:
                if "explanation" in running_dict:
                    st.markdown(f"**Explanation** : \n\n{running_dict['explanation']['function_explanation']}")
                else:
                    st.write("No explanation data available")
            with tab5:
                if "repairer" in running_dict:
                    st.markdown(f"**Repairer** : \n\n{running_dict['repairer']['repair_description']}") 
                else:
                    st.write("No repairer data available")
            with tab6:
                if "crafter" in running_dict:
                    st.markdown(f"**Crafter** : \n\n```python\n{running_dict['crafter']['improved_code']}\n```")
                else:
                    st.write("No crafter data available")
            with tab7:
                if "developer" in running_dict:
                    st.markdown(f"**Developer** : \n\n```python\n{running_dict['developer']['refactored_code']}\n```")
                else:
                    st.markdown("No developer data available")
            with tab8:
                st.markdown("**Pricing Info**")
                info_item = list(running_dict.items())[-1][1]
                token_used = info_item['token_used']
                prompt_token = info_item['prompt_token']
                completion_token = info_item['completion_token']
                cost = info_item['cost']
                
                st.markdown(f"""
                    **Info Token dan Harga**
                    
                    * Total token yang digunakan : **{token_used}**\n
                    * Prompt token yang digunakan : **{prompt_token}**\n
                    * Completion token yang digunakan : **{completion_token}**\n
                    * Perkiraan cost yaitu : **{cost} $**\n
                    """
                )
        
    if process_type=="Process the code":
        st.subheader("Input Code")   
        code = st.text_area("Enter Code", "print('Hello, World!')")
        submit = st.button("Submit Code")

        if submit:
            # if not is_query_valid(query):
            #     st.stop()
            running_dict = {}
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["All","Code", "Localizer", "Tester", "Debugger","Developer", "Price Analysis" ])
            
            with tab1:
                path="code"
                await run_code(openai_api_key, code, requirement, limit, running_dict, path, model, temperature)
            
            with tab2:
                if "upload_code" in running_dict:
                    st.markdown(f"**Code uploaded** : \n\n```python\n{running_dict['upload_code']['code']}```")
                else:
                    st.write("No code detected")
                    
            with tab3:
                if "localizer" in running_dict:
                    st.markdown(f"**Bug Detected** : \n\n{running_dict['localizer']['bug']}")
                else:
                    st.write("No localizer data available")
            
            with tab4:
                if "executer" in running_dict:
                    st.markdown(f"**Testing code** :\n\n```python\n{running_dict['executer']['testing_code']}\n```")
                else:
                    st.write("No tester data available")
            
            with tab5:
                if "debugger" in running_dict:
                    st.markdown(f"**The code after debugging** : \n\n```python\n{running_dict['debugger']['code']}\n```")
                else:
                    st.write("No debugger data available")
            
            with tab6:
                if "developer" in running_dict:
                    st.markdown(f"**The code after refactored** : \n\n```python\n{running_dict['developer']['refactored_code']}\n```")
                else:
                    st.write("No developer data available")
            
            with tab7:
                info_item = list(running_dict.items())[-1][1]
                token_used = info_item['token_used']
                prompt_token = info_item['prompt_token']
                completion_token = info_item['completion_token']
                cost = info_item['cost']
                
                st.markdown(f"""
                    **Info Token dan Harga**
                    
                    * Total token yang digunakan : **{token_used}**\n
                    * Prompt token yang digunakan : **{prompt_token}**\n
                    * Completion token yang digunakan : **{completion_token}**\n
                    * Perkiraan cost yaitu : **{cost} $**\n
                    """
                )

# Run the Streamlit app
if __name__ == "__main__":
    asyncio.run(main())
