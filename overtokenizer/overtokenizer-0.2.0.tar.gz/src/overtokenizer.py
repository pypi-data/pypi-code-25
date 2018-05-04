"""
A simple language-agnostic tokenizer based on Unicode character properties.

Copyright ® 2016, Luís Gomes <luismsgomes@gmail.com>

Simple language-independent tokenizer based on unicode character properties.
Only the following writting systems are supported:
    Latin (western Europe)
    Devanagari and Kannada (languages from India)
    Greek and Coptic
    Cyrillic (eastern Europe)
    Arabic (several languages from Africa and Asia)

As the name indicates, this tokenizer errs on the side of over-tokenization
(separating too much).
"""

import regex

__version__ = "0.2.0"


domain_regex = r"""(?:[a-z0-9\.\-_]+\.)+[a-z]{2,4}"""
user_regex = r"""[a-z0-9\.\-_]+"""
email_regex = r"""(?P<email>(?:mailto:)?{user}@{domain})"""
email_regex = email_regex.format(user=user_regex, domain=domain_regex)
url_regex = r"""(?P<url>(?:(?:ftp|http)s?://)?{domain}(?:/[^"'>\s]*)?)"""
url_regex = url_regex.format(domain=domain_regex)

ident_regex = r"""[a-z0-9]+(?:-[a-z0-9]+)?"""
ident_regex = r"""{ident}(?:\:{ident})?""".format(ident=ident_regex)
attr_regex = r"""{ident}(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^'">]*))?"""
attr_regex = attr_regex.format(ident=ident_regex)
tag_regex = r"""(?P<tag>(?:<{ident}(?:\s+{attr})*/?>|</{ident}>))"""
tag_regex = tag_regex.format(ident=ident_regex, attr=attr_regex)

num_regex = r"(?P<num>\p{N}+)"
word_regex = (
    r"""(?P<word>\p{Script=Hani}|"""  # Chinese
    r"""\p{Script=Latin}+(?:[-‐‑'’]\p{Script=Latin}+)*|"""  # European languages
    # (don't separate on hyphens or apostrophes)
    r"""\p{Script=Devanagari}+|\p{Script=Kannada}+|"""  # languages from India
    r"""(?:\p{Script=Greek}|\p{Script=Coptic})+|"""
    r"""\p{Script=Cyrillic}+|"""  # Russian
    r"""\p{Script=Arabic}+)"""
)
repeat_regex = \
    r"""(?P<repeat>[\p{P}\p{S}])( *\g<repeat>)+"""
symb_regex = r"""(?P<symb>\p{S})"""
punct_regex = r"""(?P<punct>\p{P})"""

token_regex = '{email}|{url}|{tag}|{num}|{word}|{repeat}|{symb}|{punct}'
token_regex = token_regex.format(
    email=email_regex,
    url=url_regex,
    tag=tag_regex,
    num=num_regex,
    word=word_regex,
    repeat=repeat_regex,
    symb=symb_regex,
    punct=punct_regex
)

word_char_norm = str.maketrans({
    # normalize hyphen:
    "‐": "-",
    "‑": "-",
    # normalize apostrophe:
    "’": "'",
})


class Overtokenizer:
    """Simple language-agnostic tokenizer

    >>> tokenize = Overtokenizer()
    >>> tokenize('Hello World!')
    ['Hello', 'World', '!']

    >>> tokenize = Overtokenizer(as_dicts=True)
    >>> for token in tokenize('Hello...'):
    ...     for attr in 'raw norm type start end join'.split():
    ...         print(attr, token[attr])
    ...     print("---")
    raw Hello
    norm Hello
    type word
    start 0
    end 5
    join False
    ---
    raw ...
    norm …
    type punct
    start 5
    end 8
    join True
    ---

    """

    def __init__(self, as_dicts=False):
        self.compiled_token_regex = regex.compile(token_regex, regex.U)
        self.as_dicts = as_dicts

    def __call__(self, sentence, as_dicts=None):
        """Tokenizes a single sentence.

        Newline characters are not allowed in the sentence to be tokenized.
        """
        assert isinstance(sentence, str)
        sentence = sentence.rstrip("\n")
        assert "\n" not in sentence
        tokens = []
        prev_stop = None
        for m in self.compiled_token_regex.finditer(sentence):
            type_ = m.lastgroup
            raw = m.group(0)
            if type_ == "repeat":
                norm = {
                    "...": "…",  # tranform ... into ellipsis unicode character
                    "--": "–",   # transform -- into en-dash
                    "---": "—",  # transform --- into em-dash
                    }.get(raw, None)
                if norm is None:
                    norm = raw.replace(" ", "␣")
                else:
                    type_ = "punct"
            elif type_ == "word":
                norm = raw.translate(word_char_norm)
            else:
                norm = raw
            if as_dicts or as_dicts is None and self.as_dicts:
                start = m.start()
                stop = m.end()
                join = start == prev_stop
                prev_stop = stop
                tokens.append({
                    "raw": raw,
                    "norm": norm,
                    "type": type_,
                    "start": start,
                    "stop": stop,
                    "join": join,
                })
            else:
                tokens.append(norm)
        return tokens


def untokenize(tokens):
    if not tokens:
        return ""
    text = [tokens[0]["norm"]]
    for token in tokens[1:]:
        if not token["join"]:
            text.append(" ")
        text.append(token["norm"])
    return "".join(text)


CMDLINE_USAGE = """
Usage:
    overtokenizer [--normalize] [--column <N>] [<inputfile> [<outputfile>]]
    overtokenizer --selftest
    overtokenizer --help

Options:
    --normalize, -n  Normalize the text only, without tokenizing it.
    --column <N>, -c <N>
                     Read <inputfile> as tab-separated and apply tokenizer only
                     to the specified column (first column is number 1)
    --selftest, -t   Run selftests.
    --help, -h       Show this help screen.


2016, Luís Gomes <luismsgomes@gmail.com>
"""

def main():
    from docopt import docopt
    from openfile import openfile
    args = docopt(CMDLINE_USAGE)
    if args["--selftest"]:
        import doctest
        import overtokenizer as mod
        doctest.testmod(mod)
        exit(0)
    tokenize = Overtokenizer(as_dicts=args["--normalize"])
    inputfile = openfile(args["<inputfile>"])
    outputfile = openfile(args["<outputfile>"], "wt")
    join = untokenize if args["--normalize"] else " ".join
    with inputfile, outputfile:
        if args["--column"] is not None:
            assert args["--column"].isnumeric()
            colnum = int(args["--column"])
            for line in inputfile:
                cols = line.rstrip("\n").split("\t")
                assert 1 <= column <= len(cols)
                cols[colnum - 1] = join(tokenize(cols[colnum - 1]))
                print(*cols, sep="\t", file=outputfile)
        else:
            for line in inputfile:
                print(join(tokenize(line)), file=outputfile)


if __name__ == "__main__":
    main()


__all__ = ["Overtokenizer", "__version__"]
