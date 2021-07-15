"use strict"

const mockConfiguration = {
    disableStepScreenshots: jest.fn(),
    setConfig: jest.fn()
};

const mockPage = {
    goto: jest.fn()
};

const mockSynthetics = {
    executeStep: jest.fn(),
    getConfiguration: jest.fn(() => mockConfiguration),
    getPage: jest.fn(() => mockPage)
};

module.exports = mockSynthetics;