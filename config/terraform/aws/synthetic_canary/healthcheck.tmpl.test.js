"use strict";

const { handler, executeStep, gotoUrl } = require("./healthcheck.tmpl.js");
const synthetics = require("Synthetics");
const syntheticsLogger = require("SyntheticsLogger");

describe("healthcheck", () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    // Fails by default because of the Terraform template URL strings
    test("handler", async () => {
        await expect(handler())
            .rejects
            .toThrow("Invalid URL");

        const config = synthetics.getConfiguration();
        expect(config.disableStepScreenshots.mock.calls.length).toBe(1);
        expect(config.setConfig.mock.calls.length).toBe(1);
        expect(synthetics.getPage.mock.calls.length).toBe(1);
        expect(syntheticsLogger.error.mock.calls.length).toBe(1);
    });

    test("executeStep valid", async () => {
        await executeStep(synthetics.getPage(), "http://foobar.com/status");
        expect(synthetics.executeStep.mock.calls.length).toBe(1);
    });

    test("executeStep invalid", async () => {
        await expect(executeStep({}, "muffins"))
            .rejects
            .toThrow("Invalid URL");
    });    

    test("gotoUrl success", async () => {
        const page = await synthetics.getPage();
        page.goto.mockReturnValue({
            status: () => 200,
            statusText: () => "Hello"
        });
        await gotoUrl(page, "http://foobar.com/status");
        expect(page.goto.mock.calls.length).toBe(1);
        expect(page.goto.mock.calls[0]).toEqual([
            "http://foobar.com/status", { waitUntil: ["domcontentloaded"], timeout: 30000}
        ]);
    });
    
    test("gotoUrl non-200 response", async () => {
        const page = await synthetics.getPage();
        page.goto.mockReturnValue({
            status: () => 404,
            statusText: () => "Not found"
        });
        await expect(gotoUrl(page, "http://notfound.com"))
            .rejects
            .toThrow("Failed to load url: $http://notfound.com $404 $Not found");        
    });
    
    test("gotoUrl no response", async () => {
        const page = await synthetics.getPage();
        page.goto.mockReturnValue(null);
        await expect(gotoUrl(page, "http://mysteryserver.com"))
            .rejects
            .toThrow("No response returned for url: $http://mysteryserver.com");        
    });    
})