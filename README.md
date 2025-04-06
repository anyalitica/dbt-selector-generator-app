# dbt Selector YAML Generator

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dbt-selector-generator.streamlit.app/)

## Overview

This Streamlit app helps dbt Cloud users easily generate a properly formatted `selectors.yml` file for defining complex node selection criteria. Create selectors with different definition styles, configure graph operators, build complex selection logic, and instantly copy or download the resulting YAML.

![App Screenshot](https://github.com/anyalitica/dbt-selector-generator-app/blob/main/assets/app_screenshot.png)

## Features

- **Multiple Definition Styles**: Create selectors using CLI-style, Key-value, or Full YAML formats
- **Graph Operators**: Configure + and @ operators with depth parameters
- **Complex Logic**: Build sophisticated selection criteria with unions and intersections
- **Exclusions**: Set up exclusion patterns within your selectors
- **YAML Generation**: Instantly generate well-formatted YAML with syntax highlighting
- **Documentation**: Built-in reference guides for selector methods, graph operators, and examples

## Why Use Selectors?

YAML selectors provide several benefits:
- **Legibility**: Complex selection criteria are more readable in YAML
- **Version Control**: Selector definitions stored in your git repository
- **Reusability**: Reference selectors in multiple job definitions
- **Complexity Management**: Build sophisticated selection logic that would be unwieldy on the command line

## Getting Started

1. Visit the [live app](https://dbt-selector-generator.streamlit.app/)
2. Create one or more selectors using the form
3. Copy or download the generated YAML
4. Place the content in a file named `selectors.yml` at the top level of your dbt project
5. Use your selectors in job commands with `dbt run --selector my_selector`

## Documentation

The app includes comprehensive documentation on:
- **Selector Methods**: All dbt node selection methods and their usage
- **Graph Operators**: Understanding + and @ operators
- **Set Operators**: How to use union and intersection logic
- **Complex Structures**: Building nested selection criteria
- **Examples**: Real-world selector examples and use cases

## Local Development

To run the app locally:

```bash
# Clone the repository
git clone https://github.com/anyalitica/dbt-selector-generator-app.git
cd dbt-selector-generator-app

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Requirements

- Python 3.7+
- Streamlit
- PyYAML

## Contributions

Contributions are welcome! Please submit any issues or suggestions for this app on the [GitHub issues page](https://github.com/anyalitica/dbt-selector-generator-app/issues?q=is%3Aissue).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Designed by: Anya Prosvetova, [anyalitica.dev](https://anyalitica.dev)