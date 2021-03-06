import ui

def main():
    """Main function"""
    def import_agent():
        """Wrapper for threaded action to import the agent module into global namespace"""
        globals()["agent"] = __import__("agent")

    ui.threaded_action(import_agent, "Loading program")

    if agent.welcome():
        agent.get_query()

if __name__ == "__main__":
    main()
