from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-max",
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    openai_api_key="sk-ws-H.EMYXMXM.Ioel.MEQCIHQ2dwzvrHhHLtJ3PRFFhX8ZKotrZRQMzT3jGnxs1vTzAiBqa8J39BLj3eK95R2lofTIL4EDaCAXmpqnvSo-ZEBxfw"
)
response = llm.invoke("你好，请介绍一下自己")
print(response.content)