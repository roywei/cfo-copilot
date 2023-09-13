from langchain.prompts import PromptTemplate

metric_prompt_template = PromptTemplate(
    input_variables=["metric"],
    template="""
now calculate the value of {metric} and it's delta over last time period, return in json schema of 
{
"value":, "",
"delta": ""
}
Your response should look like this:
{
"value": "23.5",
"delta": "1.2"
}
""",
)
