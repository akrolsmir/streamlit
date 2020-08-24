# Copyright 2018-2020 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st

CAT_IMG = "https://images.unsplash.com/photo-1552933529-e359b2477252?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=950&q=80"
DOG_IMG = "https://images.unsplash.com/photo-1534361960057-19889db9621e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80"
RABBIT_IMG = "https://images.unsplash.com/photo-1580762410711-aa47eb8872d7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80"


with st.echo("below"):
    # Let's lay out our page!
    top = st.container()
    c1, c2, c3 = st.columns(3)

    # Now use a column like st.sidebar...
    c1.header("First column")
    c1.image(CAT_IMG, use_column_width=True)

    # Or use the fancy new `with` notation!
    with c2:
        "## Second column"
        st.image(DOG_IMG, use_column_width=True)
    with c3:
        st.header("Third column")
        st.image(RABBIT_IMG, use_column_width=True)

    # st.container() is like st.empty() but for *multiple* things
    with top:
        st.title("Horizontal Layout Playground")
        "*Press 'e' to edit this page!*"
        """
        Featuring:
        - `st.container`: Write elements to an out-of-order block
        - `st.columns`: Create multiple side-by-side containers
        - `with`: Syntax sugar
        """

# def my_widget(test):
#     s = st.slider(f"Test result: {test}", key=test)
#     c = st.checkbox("10 points of extra credit?", key=test)
#     score = s + 10 if c else 0
#     f"You got {score} points!"
#     return score


# c1, c2, c3 = st.beta_columns(3)
# with c1:
#     midterm = my_widget("midterm")
# with c3:
#     final = my_widget("final")
# with c2:
#     f"Midterm: {midterm}, Final: {final}"
