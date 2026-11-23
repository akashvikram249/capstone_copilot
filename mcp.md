# Jira MCP setup

Use this only after confirming with EPAM that the Atlassian MCP endpoint is approved for the internal Jira site at `https://jiraeu.epam.com`.

The workspace MCP configuration is in [`.mcp.json`](.mcp.json). VS Code Copilot may require the experimental `chat.mcp.workspaceRootConfig.enabled` setting to load a workspace-root config. Alternatively, add the endpoint through **MCP: Add Server** and choose **Global > Copilot Global** for a personal configuration (`~/.copilot/mcp-config.json`, or `$COPILOT_HOME/mcp-config.json` when set).

The config contains only an environment-variable reference, not a credential:

```json
{
  "mcpServers": {
    "atlassian": {
      "type": "http",
      "url": "https://mcp.atlassian.com/v2/mcp",
      "headers": {
        "Authorization": "Basic ${ATLASSIAN_MCP_BASIC}"
      }
    }
  }
}
```

Set `ATLASSIAN_MCP_BASIC` in the environment available to the Copilot process, using an organization-approved secret mechanism. Its value should be only the Base64-encoded email-and-token portion; do not include the `Basic ` prefix. Base64 is reversible and does not protect a credential. Environment variables are also not a secret vault, so use OAuth instead if the approved server supports it.

Never paste credentials into chat, commit them to the repository, or add populated authorization headers to this file. If a real token was shared or exposed, revoke it and create a replacement. After setup, verify the connection with a read-only request for an issue you are authorized to view.
