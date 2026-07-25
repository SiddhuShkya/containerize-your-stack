require('dotenv').config();
const { createApp } = require("./src/app.js");

const app = createApp();
app.set("json spaces", 2); // pretty-print JSON responses

const port = process.env.PORT || 3000;

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`)
})