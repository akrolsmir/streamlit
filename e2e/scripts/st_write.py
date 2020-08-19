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

with st.echo("below"):
    with st.sidebar:
        st.write("Markdown")
        "# magic"
    "And now I'm free!"

    c1, c2, c3 = st.beta_columns(3)
    c1.title("First column")
    with c2:
        "## Second column"
    c3.slider("Third column")

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
