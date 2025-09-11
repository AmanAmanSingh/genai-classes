import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o-mini")

TEXT = "Hello, world!"
res = encoding.encode(TEXT)


print("ENCODE RES", res)
print("DECODE RES", encoding.decode(res))
