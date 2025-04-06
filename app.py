import streamlit as st
import yaml
# import pyperclip
from typing import Dict, List, Any, Optional, Union

st.set_page_config(
    page_title="dbt Selector YAML Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("dbt Selector YAML Generator")
    st.markdown("""
    Create a structured `selector.yml` file for your dbt Cloud projects. 
    Configure your selectors with a user-friendly interface and generate valid YAML code.
    """)
    
    st.sidebar.title("Navigation")
    
    # Main sections in the sidebar
    section = st.sidebar.radio(
        "",
        ["Selector configuration", "Docs & Examples", "About"]
    )
    
    if section == "Selector configuration":
        selector_config_section()
    elif section == "Docs & Examples":
        documentation_section()
    else:
        about_section()

def create_criterion_section(key_prefix="", level=0, is_exclude=False):
    """Create a form section for defining a selection criterion"""
    criterion = {}
    
    # Choose criterion type based on complexity
    criterion_type = st.selectbox(
        "Type",
        ["Simple Method", "Complex Structure"],
        key=f"{key_prefix}_type_{level}"
    )
    
    if criterion_type == "Simple Method":
        method = st.selectbox(
            "Method",
            ["tag", "path", "package", "config", "fqn", "resource_type", "source", 
             "exposure", "metric", "state", "group", "access", "file", "saved_query", 
             "semantic_model", "source_status", "result", "test_name", "version"],
            key=f"{key_prefix}_method_{level}"
        )
        
        value = st.text_input("Value", key=f"{key_prefix}_value_{level}")
        
        # Graph operators
        col1, col2 = st.columns(2)
        with col1:
            children = st.checkbox("Include children", key=f"{key_prefix}_children_{level}")
            if children:
                children_depth = st.number_input("Children depth", 
                                                min_value=1, value=1, 
                                                key=f"{key_prefix}_children_depth_{level}")
        
        with col2:
            parents = st.checkbox("Include parents", key=f"{key_prefix}_parents_{level}")
            if parents:
                parents_depth = st.number_input("Parents depth", 
                                               min_value=1, value=1, 
                                               key=f"{key_prefix}_parents_depth_{level}")
        
        childrens_parents = st.checkbox("Include children's parents (@ operator)", 
                                       key=f"{key_prefix}_childrens_parents_{level}")
        
        # Indirect selection
        indirect_selection = st.selectbox(
            "Indirect selection",
            ["eager", "cautious", "buildable", "empty"],
            help="Controls how tests are indirectly selected",
            key=f"{key_prefix}_indirect_{level}"
        )
        
        # Build criterion
        criterion = {
            "method": method,
            "value": value
        }
        
        if children:
            criterion["children"] = True
            criterion["children_depth"] = children_depth
        
        if parents:
            criterion["parents"] = True
            criterion["parents_depth"] = parents_depth
        
        if childrens_parents:
            criterion["childrens_parents"] = True
        
        criterion["indirect_selection"] = indirect_selection
        
    else:  # Complex Structure
        operation = st.selectbox(
            "Operator",
            ["union", "intersection"],
            help="Union = OR, Intersection = AND",
            key=f"{key_prefix}_operation_{level}"
        )
        
        # For each operation, allow 2+ sub-criteria
        num_subcriteria = st.number_input(
            f"Number of {operation} elements", 
            min_value=2, max_value=10, value=2,
            key=f"{key_prefix}_num_sub_{level}"
        )
        
        subcriteria = []
        for i in range(int(num_subcriteria)):
            st.markdown(f"#### {operation.capitalize()} Element {i+1}")
            
            # Create a collapsible section for each sub-criterion
            with st.expander(f"Configure {operation} element {i+1}"):
                # Recursively create subcriteria with a new prefix to ensure unique keys
                subcriterion = create_criterion_section(
                    key_prefix=f"{key_prefix}_{operation}_{i}",
                    level=level+1
                )
                subcriteria.append(subcriterion)
        
        criterion[operation] = subcriteria
    
    # Exclusions (only for non-exclude criteria to avoid nesting excludes inside excludes)
    if not is_exclude:
        add_exclusion = st.checkbox("Add exclusions", key=f"{key_prefix}_add_excl_{level}")
        
        if add_exclusion:
            st.subheader("Exclusions")
            num_exclusions = st.number_input(
                "Number of exclusions", min_value=1, max_value=5, value=1,
                key=f"{key_prefix}_num_excl_{level}"
            )
            
            exclusions = []
            for i in range(int(num_exclusions)):
                st.markdown(f"#### Exclusion {i+1}")
                with st.expander(f"Configure exclusion {i+1}"):
                    # Create exclusion criteria (recursively, but marked as an exclusion)
                    exclusion = create_criterion_section(
                        key_prefix=f"{key_prefix}_excl_{i}",
                        level=level+1,
                        is_exclude=True
                    )
                    exclusions.append(exclusion)
            
            if exclusions:
                criterion["exclude"] = exclusions
    
    return criterion

def selector_config_section():
    st.header("Selector configuration")
    
    # Initialize selectors list in session state if not present
    if 'selectors' not in st.session_state:
        st.session_state.selectors = []
    
    # Simple selector form for basic information
    with st.form("selector_info_form"):
        st.subheader("Basic selector information")
        selector_name = st.text_input("Selector name", "my_selector")
        selector_description = st.text_input("Description", "Custom selector for specific models")
        is_default = st.checkbox("Set as default selector")
        
        # Submit button only for basic info
        info_submitted = st.form_submit_button("Continue to definition")
    
    if info_submitted or 'current_selector_info' in st.session_state:
        # Save the basic info in session state
        if info_submitted:
            st.session_state.current_selector_info = {
                "name": selector_name,
                "description": selector_description,
                "default": is_default
            }
        
        # Now display the definition section
        st.subheader(f"Define selection logic for '{st.session_state.current_selector_info['name']}'")
        
        # Definition type selection
        definition_type = st.radio(
            "Definition type",
            ["CLI-style", "Key-value", "Full YAML"],
            help="Choose how you want to define your selector"
        )
        
        if definition_type == "CLI-style":
            with st.form("cli_form"):
                cli_definition = st.text_input(
                    "CLI-style Definition", 
                    "tag:nightly",
                    help="Simple string format like 'tag:nightly' or 'path:models/staging'"
                )
                definition = cli_definition
                
                cli_submitted = st.form_submit_button("Add Selector")
                
                if cli_submitted:
                    selector = st.session_state.current_selector_info.copy()
                    selector["definition"] = definition
                    st.session_state.selectors.append(selector)
                    if 'current_selector_info' in st.session_state:
                        del st.session_state.current_selector_info
                    st.success(f"Selector '{selector['name']}' added!")
                    st.rerun()
                
        elif definition_type == "Key-value":
            with st.form("kv_form"):
                method = st.selectbox(
                    "Method",
                    ["tag", "path", "package", "config", "fqn", "resource_type", "source", "exposure", "metric", "state", "group"]
                )
                value = st.text_input("Value", "nightly")
                definition = {method: value}
                
                kv_submitted = st.form_submit_button("Add Selector")
                
                if kv_submitted:
                    selector = st.session_state.current_selector_info.copy()
                    selector["definition"] = definition
                    st.session_state.selectors.append(selector)
                    if 'current_selector_info' in st.session_state:
                        del st.session_state.current_selector_info
                    st.success(f"Selector '{selector['name']}' added!")
                    st.rerun()
                
        else:  # Full YAML
            st.write("Define the selection criteria for your selector:")
            
            # Create a complex structure for the definition using our recursive function
            definition = create_criterion_section(key_prefix="root", level=0)
            
            # Add selector button
            if st.button("Add Selector"):
                selector = st.session_state.current_selector_info.copy()
                selector["definition"] = definition
                st.session_state.selectors.append(selector)
                if 'current_selector_info' in st.session_state:
                    del st.session_state.current_selector_info
                st.success(f"Selector '{selector['name']}' added!")
                st.rerun()
    
    # Display current selectors
    if st.session_state.selectors:
        st.header("Current selectors")
        
        for i, selector in enumerate(st.session_state.selectors):
            with st.expander(f"Selector: {selector['name']}"):
                st.json(selector)
                if st.button(f"Remove selector {i+1}", key=f"remove_{i}"):
                    st.session_state.selectors.pop(i)
                    st.rerun()
    
    # Generate final YAML
    if st.session_state.selectors:
        st.header("Generated selectors.yml")
        yaml_content = {"selectors": st.session_state.selectors}
        yaml_str = yaml.dump(yaml_content, sort_keys=False, default_flow_style=False)

        # Display the YAML with built-in copy button
        st.code(yaml_str, language="yaml")

        # Add instructional text about the copy button
        st.caption("ℹ️ Click the copy icon in the top-right corner of the code block to copy the YAML to your clipboard.")

        # Provide just the download button
        st.download_button(
            label="Download YAML",
            data=yaml_str,
            file_name="selectors.yml",
            mime="text/yaml"
        )

        st.header("Reset Configuration")
        if st.button("Clear all selectors and start over", type="primary", use_container_width=True):
            # Clear all relevant session state variables
            for key in list(st.session_state.keys()):
                if key in ['selectors', 'current_selector_info']:
                    del st.session_state[key]
            st.success("All configurations cleared!")
            st.rerun()


def documentation_section():
    st.header("dbt selector documentation")
    
    tabs = st.tabs([
        "Selector Methods", 
        "Graph Operators", 
        "Set Operators",
        "Complex Structures",
        "Examples"
    ])
    
    with tabs[0]:
        st.markdown("""
        ## Node selector methods
        
        Selector methods return all resources that share a common property, using the syntax `method:value`.
        
        | Method | Description | Example |
        | --- | --- | --- |
        | access | Selects models based on their access property | `access:public` |
        | config | Selects models that match a specified node config | `config.materialized:incremental` |
        | exposure | Selects parent resources of a specified exposure | `+exposure:weekly_kpis` |
        | file | Selects a model by its filename | `file:some_model.sql` |
        | fqn | Selects nodes based on their fully qualified names | `fqn:your_project.some_model` |
        | group | Selects models defined within a group | `group:finance` |
        | metric | Selects parent resources of a specified metric | `+metric:weekly_active_users` |
        | package | Selects models defined within a package | `package:snowplow` |
        | path | Selects models/sources defined at or under a specific path | `path:models/staging/github` |
        | resource_type | Selects nodes of a particular type | `resource_type:exposure` |
        | result | Selects resources based on result status from a prior run | `result:error` |
        | saved_query | Selects saved queries | `saved_query:*` |
        | semantic_model | Selects semantic models | `semantic_model:*` |
        | source | Selects models that select from a specified source | `source:snowplow+` |
        | source_status | References source freshness results | `source_status:fresher+` |
        | state | Selects nodes by comparing against a previous version | `state:modified` |
        | tag | Selects models that match a specified tag | `tag:nightly` |
        | test_name | Selects tests based on the name of the generic test | `test_name:unique` |
        | version | Selects versioned models based on their version identifier | `version:latest` |
        
        [Full method documentation](https://docs.getdbt.com/reference/node-selection/methods)
        """)
    
    with tabs[1]:
        st.markdown("""
        ## Graph operators
        
        Graph operators allow you to select parents or children of resources in the DAG.
        
        | Operator | Description | Example |
        | --- | --- | --- |
        | + (after) | Includes the resource and all its descendants | `my_model+` |
        | + (before) | Includes the resource and all its ancestors | `+my_model` |
        | + (both) | Includes the resource, all ancestors and descendants | `+my_model+` |
        | @ | Similar to +, but includes all ancestors of all descendants | `@my_model` |
        | n+ | Adjusts the number of edges to follow | `2+my_model` (grandparents) |
        
        [Graph operators documentation](https://docs.getdbt.com/reference/node-selection/graph-operators)
        """)
    
    with tabs[2]:
        st.markdown("""
        ## Set operators
        
        Set operators allow you to combine multiple selection criteria.
        
        | Operator | Description | Example |
        | --- | --- | --- |
        | space | Union (select if in any of the sets) | `model_a model_b` |
        | comma | Intersection (select if in all sets) | `model_a,model_b` |
        
        In YAML format, these are represented by the `union` and `intersection` keywords.
        
        [Set operators documentation](https://docs.getdbt.com/reference/node-selection/set-operators)
        """)
    
    with tabs[3]:
        st.markdown("""
        ## Complex structures
        
        In YAML selectors, you can define complex selection logic using nested unions and intersections.
        
        ### Union (OR logic)
        
        Selects resources that match ANY of the criteria:
        
        ```yaml
        selectors:
          - name: union_example
            definition:
              union:
                - method: tag
                  value: nightly
                - method: path
                  value: models/core
        ```
        
        ### Intersection (AND logic)
        
        Selects resources that match ALL of the criteria:
        
        ```yaml
        selectors:
          - name: intersection_example
            definition:
              intersection:
                - method: tag
                  value: nightly
                - method: config.materialized
                  value: incremental
        ```
        
        ### Nested operations
        
        You can nest unions and intersections to create complex logic:
        
        ```yaml
        selectors:
          - name: complex_example
            definition:
              union:
                - intersection:
                    - method: tag
                      value: nightly
                    - method: config.materialized
                      value: incremental
                - method: path
                  value: models/critical
                - exclude:
                    - method: tag
                      value: deprecated
        ```
        
        [YAML selectors documentation](https://docs.getdbt.com/reference/node-selection/yaml-selectors)
        """)
    
    with tabs[4]:
        st.markdown("""
        ## Examples
        
        ### Example 1: Models for nightly batch processing
                    
        This selector will include models that match any of the following criteria:
        - Models tagged with `nightly`
        - Models that are both:
        - Located in the `models/marts` directory path
        - Configured with `materialized: incremental`
        - But will exclude any models that have the tag `skip_batch`            
        
        ```yaml
        selectors:
          - name: nightly_batch
            description: "Models to run in nightly batch job"
            definition:
              union:
                - method: tag
                  value: nightly
                - intersection:
                    - method: path
                      value: models/marts
                    - method: config.materialized
                      value: incremental
                - exclude:
                    - method: tag
                      value: skip_batch
        ```
        
        ### Example 2: Critical models and their dependencies
                    
        This selector will include:
        - Models tagged with `critical` AND all of their parent models (dependencies)
        - Models referenced by the `executive_dashboard` exposure AND all of their parent models (dependencies)

        This configuration ensures you run not just the critical models but everything they depend on as well.            
        
        ```yaml
        selectors:
          - name: critical_path
            description: "Critical models and their dependencies"
            definition:
              union:
                - method: tag
                  value: critical
                  parents: true
                - method: exposure
                  value: executive_dashboard
                  parents: true
        ```
        
        ### Example 3: Test selection

        This selector uses a combination of `intersection` and `union` operators to create a logical selection structure that will include:

        Tests that meet BOTH of these criteria:
        1. Are of resource type "test" (this selects only test resources)
        2. AND match AT LEAST ONE of the following:
        - Located in the `models/core` directory path
        - Tagged with `critical_test`            


        ```yaml
        selectors:
          - name: core_tests
            description: "Tests for core models"
            definition:
              intersection:
                - method: resource_type
                  value: test
                - union:
                    - method: path
                      value: models/core
                    - method: tag
                      value: critical_test
        ```
        
        [More examples in dbt documentation](https://docs.getdbt.com/reference/node-selection/yaml-selectors)
        """)

def about_section():
    st.markdown("""
    This tool helps dbt Cloud users generate a properly formatted `selector.yml` file that follows dbt's documentation and best practices, specifically:
    
    - Create selectors with different definition styles (CLI, Key-value, Full YAML)
    - Configure graph operators like + and @
    - Build complex selection criteria with unions and intersections
    - Set up exclusions for your selectors
    - Copy and download the generated YAML
                
    ### Getting started
    
    1. Create one or more selectors using the form
    2. Copy or download the generated YAML
    3. Place the content in a file named `selectors.yml` at the top level of your dbt project
    4. Use your selectors in job commands with `dbt run --selector my_selector`                            
                    
    ### Why use selectors?
    
    YAML selectors provide several benefits:
    - **Legibility:** complex selection criteria are more readable
    - **Version control:** selector definitions can be stored in your git repository
    - **Reusability:** selectors can be referenced in multiple job definitions
    - **Complexity management:** build sophisticated selection logic that would be unwieldy on the command line

    [Learn more about dbt YAML selectors](https://docs.getdbt.com/reference/node-selection/yaml-selectors)            
                
    ### Credits

    Designed by: Anya Prosvetova, [anyalitica.dev](https://anyalitica.dev)
                
    Please submit any issues or suggestions for this app on the [GitHub issues page](https://github.com/anyalitica/dbt-selector-generator-app/issues?q=is%3Aissue).            
    """)

if __name__ == "__main__":
    main()