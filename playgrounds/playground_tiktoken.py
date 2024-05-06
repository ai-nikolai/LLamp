import tiktoken

def calculate_tokens(text, model_name):
    """Calculate the number of tokens for a given text and model."""
    try:
        model_name_clean = "-".join(model_name.split("-")[:2])
        try:
            encoding = tiktoken.encoding_for_model(model_name_clean)
        except KeyError as e:
            print(e)
            encoding = tiktoken.get_encoding("cl100k_base")
        encoding2 = tiktoken.get_encoding(encoding.name)
        assert encoding2==encoding, "Encodings are different."
        return len(encoding.encode(text))
    except Exception as e:
        (f"Failed to retrieve 'cl100k_base' encoding: {e}")
        raise


if __name__=="__main__":
    enc = tiktoken.get_encoding("cl100k_base")
    assert enc.decode(enc.encode("hello world")) == "hello world"

    token_count = calculate_tokens("HI asdfфыващшозйщо фывадлжофыжва بشسيكبمشتخضهحردضحخهصرسنشكيمبت 日；尸中木大火車站明日之內將就一下就好啦好無事實問題🙋‍♀️我這你  千寿針ヌフあ奴あウリの愛知 asdlkfjpoqijp Now this is an interesting test","gpt-3.5-0125")
    print(token_count)