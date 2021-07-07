"use strict";

const { URL } = require("url");
const synthetics = require("Synthetics");
const log = require("SyntheticsLogger");
const syntheticsConfiguration = synthetics.getConfiguration();

/**
 * Main handler for the healthcheck canary.  Loops over the `const urls` 
 * and attempts to load the given page in Puppeteer.  Any HTTP resonse
 * code outside of the 200 range is considered a failure.
 */
const handler = async function () {

    syntheticsConfiguration.disableStepScreenshots();
    syntheticsConfiguration.setConfig({
       continueOnStepFailure: true
    });
 
    let page = await synthetics.getPage();
    
    for (const url of urls) {
        await executeStep(page, url);
    }
};

/**
 * Parses the given url and executes the canary step.
 * @param {Object} page Puppeteer page object
 * @param {String} url URL to load
 */
const executeStep = async function (page, url) {
    let stepName = null;
 
    try {
        stepName = new URL(url).hostname;
    } catch (error) {
        log.error(`Error parsing url: $${url}.  $${error}`);
        throw error;
    }
    
    await synthetics.executeStep(stepName, async function () {
        await gotoUrl(page, url);
    });
};

/**
 * Attempts to load the given URL.  HTTP response code must be in the 200 range
 * to be considered a success.
 * @param {Object} page Puppeteer page object 
 * @param {String} url URL to load
 */
const gotoUrl = async function (page, url) {
    const response = await page.goto(url, { waitUntil: ["domcontentloaded"], timeout: 30000});
    if (response) {
        const status = response.status();
        const statusText = response.statusText(); 
        if (status < 200 || status > 299) {
            throw new Error(`Failed to load url: $${url} $${status} $${statusText}`); 
        }
    } else {
        const logNoResponseString = `No response returned for url: $${url}`;
        log.error(logNoResponseString);
        throw new Error(logNoResponseString);
    }
}

const urls = [
    "${healthcheck_url_en}", 
    "${healthcheck_url_fr}"
];
 
exports.handler = async () => {
    return await handler();
};
exports.executeStep = executeStep;
exports.gotoUrl = gotoUrl;