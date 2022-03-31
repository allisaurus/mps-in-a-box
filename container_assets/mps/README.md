# RELEASE BUILD GOES IN THIS FOLDER

* include the `server.cfg` and `client.cfg` files used to run each launcher
* include a valid `engine.json` file so the project doesn't try to look for it higher up in the file system from within the container (b/c there won't be one)