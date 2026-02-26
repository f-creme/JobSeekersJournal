import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

from src.jobjournal.jobjournal_gui import main

if __name__=="__main__":
    main()