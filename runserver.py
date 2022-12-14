"""Starts the server to process http requests"""

import sys
from majorapp import app

def main():
    """Enables http server on specified port"""    

    # Ensures prooper port usage
    try:
        port = int(sys.argv[1])
    except ValueError:
        print('Port must be an integer.', file=sys.stderr)
        sys.exit(1)

    # Runs the web app on specified port
    try:
        app.run(host='localhost', port=port, debug=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
