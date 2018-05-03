import sys

if __name__ == "__main__":
    from selenium import webdriver
    from robot_md_launcher import SeleniumIDERunner

    driver = webdriver.Chrome()
    args = sys.argv[1:]
    SeleniumIDERunner.run_markdown_file(args, driver)
