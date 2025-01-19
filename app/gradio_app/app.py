"""
Gradio app for searching property information.

"""

import gradio as gr

from indexes.index_query import QueryEngineSingleton
from utilities.custom_logger import logger


def run_query(user_input):
    """
    For demonstration purposes, we'll just echo the input.
    """
    query_engine_instance = QueryEngineSingleton()
    logger.debug(f"Query: {user_input}")
    response = query_engine_instance.query(user_input)
    logger.debug(f"Response: {response}")
    return str(response)


def search_function(user_input, history):
    """
    Called when "Search" button is clicked or Enter is pressed.
      1) Compute the system output for the new input.
      2) Update the history (limit to 10 items).
      3) Return:
         - The new system output
         - The updated history
         - The updated dropdown choices
    """
    result = run_query(user_input)

    # If already at 10 items, remove the oldest
    if len(history) >= 10:
        history.pop(0)

    # Add the new (query, result)
    history.append((user_input, result))

    # Update dropdown choices (just the queries)
    dropdown_choices = [h[0] for h in history]

    return result, history, gr.update(choices=dropdown_choices)


def select_history(selected_query, history):
    """
    Called when the user picks a query from the dropdown.
    We want to:
      - Fill the 'History Query' field with that query.
      - NOT touch the "System Output."
    """
    if not selected_query or not history:
        return ""

    # Find the most recent matching query in the history
    for query, answer in reversed(history):
        if query == selected_query:
            return answer

    return ""


def main():
    logger.info("Starting Gradio app...")
    with gr.Blocks() as demo:
        gr.Markdown("## Property RAG Search - Collin County zip code 75024")

        # State to store (query, result) pairs
        history_state = gr.State([])

        # Load the index
        _ = QueryEngineSingleton()

        # We split the UI into two sections (frames/groups)
        with gr.Row():
            # Frame 1: "Enter your query" & "System Output"
            with gr.Group():
                input_field = gr.Textbox(label="Enter your query")
                search_button = gr.Button("Search")
                output_field = gr.Textbox(label="System Output")

            # Frame 2: "History (last 10 queries)" & "History Query"
            with gr.Group():
                history_dropdown = gr.Dropdown(
                    label="History (last 10 queries)", choices=[], interactive=True
                )
                history_input_field = gr.Textbox(
                    label="History Query", interactive=False
                )

        # 1) SEARCH BUTTON:
        #    When clicked, run search_function
        search_button.click(
            fn=search_function,
            inputs=[input_field, history_state],
            outputs=[output_field, history_state, history_dropdown],
        )

        # 2) TRIGGER SEARCH WHEN "ENTER" IS PRESSED INSIDE input_field
        input_field.submit(
            fn=search_function,
            inputs=[input_field, history_state],
            outputs=[output_field, history_state, history_dropdown],
        )

        # 3) HISTORY SELECTION:
        #    When the user picks a past query, ONLY update 'History Query' field.
        #    The 'System Output' remains unchanged.
        history_dropdown.change(
            fn=select_history,
            inputs=[history_dropdown, history_state],
            outputs=history_input_field,
        )

    demo.launch(share=False, show_api=False)


if __name__ == "__main__":
    main()
