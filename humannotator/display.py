# third party
from IPython.display import HTML, display, clear_output


class Display(object):
    style = """
        * {
            box-sizing: border-box;
        }
        h1, h2, h3, h4, p, .container {
            margin: 0 !important;
            padding: 12px;
        }
        h1 {
            background-color: black;
            color: white;
            text-transform: uppercase;
        }
        hr {
            margin: 0 !important;
            border: none;
            border-top: 1px solid black;
        }
        .box {
            border: 1px solid black;
        }
        .container {
            overflow: scroll;
        }
        """

    def get_html(self, sample, idx, row):
        info_html = ''
        if self.phrase_info is not None:
            info_html = self.phrase_info.to_html(
                index=False,
                notebook=True
                )
            info_html = f"<div class='container'>{info_html}</div>"

        sample_html = ''
        if sample:
            sample_html += f"SAMPLE: {sample} of {self.n_samples} | "

        content = (
            f"<h1>{self.name}</h1>"
            f"<h2>PHRASE: {self.phrase}</h2>"
            f"{info_html}"
            f"<h3>"
            f"{sample_html}"
            f"SOURCE: {row.source} | "
            f"RESULT: {idx + 1} of {self.n_results} | "
            f"{row.id}"
            f"</h3><hr>"
            f"<h4>{row.title}</h4><hr>"
            )

        for p in row.body_:
            if re.search(self.regex, p):
                p = f"<p>{p}</p>"
                content += re.sub(
                    self.regex,
                    f"<mark><b>{self.phrase}</b></mark>",
                    p,
                    )
        return f"<style>{self.style}</style><div class='box'>{content}</div>"
