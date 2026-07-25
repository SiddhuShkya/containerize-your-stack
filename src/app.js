
const express = require("express");
const swaggerUI = require("swagger-ui-express");
const openapi = require("../openapi.json");

const metaRoutes = require("./routes/meta.routes.js");
const taskRoutes = require("./routes/tasks.routes.js");
const { errorHandler } = require("./middleware/error-handler.js");

function createApp() {
    const app = express();

    app.use(express.json())
    app.use("/docs", swaggerUI.serve, swaggerUI.setup(openapi));

    app.use("/", metaRoutes);
    app.use("/", taskRoutes);

    app.use(errorHandler);

    return app;
}

module.exports = { createApp };
