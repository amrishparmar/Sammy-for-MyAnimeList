def main():
    def import_agent():
        """Wrapper for threaded action to import the agent module into global namespace"""
        globals()["agent"] = __import__("agent")

    import ui
    ui.threaded_action(import_agent, "Loading program")

    if agent.welcome():
        agent.get_query()

if __name__ == "__main__":
    main()
