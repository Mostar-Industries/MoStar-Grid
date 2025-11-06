// src/moscripts/MoScript.ts

/**
 * Defines the structure for a MoScript, a self-contained, executable unit of logic
 * within the MoStar GRID symbolic AI system. Each MoScript is designed to be modular,
 * triggerable, and validated against the system's covenant.
 */
export interface MoScript<T = any, R = any> {
    /**
     * A unique identifier for the MoScript, following the 'mo-<name>-<version>' pattern.
     * @example "mo-user-authentication-v1"
     */
    id: string;

    /**
     * A human-readable name for the MoScript.
     * @example "User Authentication Handler"
     */
    name: string;

    /**
     * The event or condition that triggers the execution of this MoScript.
     * @example "onUserLoginAttempt"
     */
    trigger: string;

    /**
     * An array of strings representing the names of the inputs required by the logic.
     * These are keys that will be present in the object passed to the `logic` function.
     * @example ["username", "password"]
     */
    inputs: string[];

    /**
     * The core logic of the MoScript. A function that takes an object of inputs
     * and returns a result. This function can be asynchronous.
     * @param inputs An object containing the data required for the script's execution.
     * @returns The result of the script's execution.
     */
    logic: (inputs: T) => R | Promise<R>;

    /**
     * A function that generates a human-readable, covenant-aligned message
     * based on the result of the `logic` function. This is used for logging,
     * UI feedback, or communication with other agents.
     * @param result The output from the `logic` function.
     * @returns A string message.
     * @example (result) => `Authentication for user ${result.user} status: ${result.status}`
     */
    voiceLine: (result: R) => string;
    
    /**
     * Soul-Aligned Security Scan. If true, the script's execution is subject to
     * rigorous security and covenant validation by the Verdict Engine.
     * Set to `false` only for trivial, non-sensitive operations.
     */
    sass: boolean;
}

/** Optional metadata that can accompany a MoScript at registration time. */
export interface MoScriptMeta {
  author?: string;
  soulprint?: string;
  topic?: string; // e.g., "health", "finance", "politics", "security"
}

/**
 * The ScrollValidator is responsible for ensuring that all MoScripts adhere to the
 * structural and covenantal rules of the MoStar GRID. It acts as a gatekeeper
 * before a script is registered or executed.
 */
export class ScrollValidator {
    /** Regex enforcing 'mo-<kebab>-v<integer>' or '-v<number>' variants. */
    private static ID_RX = /^mo-[a-z0-9]+(?:-[a-z0-9]+)*-v\d+$/;

    /**
     * Validates a single MoScript object against a set of predefined rules.
     * Throws an error if validation fails.
     * @param script The MoScript to validate.
     * @returns True if the script is valid.
     */
    static validate(script: MoScript): boolean {
        if (!script.id || typeof script.id !== 'string' || !script.id.startsWith('mo-')) {
            throw new Error(`Invalid MoScript ID: "${script.id}". Must be a string starting with "mo-".`);
        }
        if (!this.ID_RX.test(script.id)) {
            throw new Error(`MoScript ID does not match pattern 'mo-<name>-v<number>': "${script.id}"`);
        }
        if (!script.name || typeof script.name !== 'string') {
            throw new Error(`Invalid MoScript Name for ID "${script.id}". Must be a non-empty string.`);
        }
        if (!script.trigger || typeof script.trigger !== 'string') {
            throw new Error(`Invalid MoScript Trigger for ID "${script.id}". Must be a non-empty string.`);
        }
        if (!Array.isArray(script.inputs) || !script.inputs.every(x => typeof x === 'string')) {
            throw new Error(`Invalid MoScript Inputs for ID "${script.id}". Must be an array of strings.`);
        }
        if (typeof script.logic !== 'function') {
            throw new Error(`Invalid MoScript Logic for ID "${script.id}". Must be a function.`);
        }
        if (typeof script.voiceLine !== 'function') {
            throw new Error(`Invalid MoScript VoiceLine for ID "${script.id}". Must be a function.`);
        }
        if (typeof script.sass !== 'boolean') {
             throw new Error(`Invalid MoScript SASS flag for ID "${script.id}". Must be a boolean.`);
        }

        // Soft checks: attempt to prevent disallowed constructs from appearing in source.
        const src = script.logic.toString();
        const bad = /(\beval\s*\()|(\bFunction\s*\()|(child_process)|(process\.exec\b)/;
        if (bad.test(src)) {
            throw new Error(`Logic for "${script.id}" contains forbidden constructs.`);
        }

        return true;
    }

    /**
     * Validates an array of MoScripts.
     * @param scripts An array of MoScripts to validate.
     * @returns True if all scripts are valid.
     */
    static validateScroll(scripts: MoScript[]): boolean {
        const seen = new Set<string>();
        for (const script of scripts) {
            this.validate(script);
            if (seen.has(script.id)) {
                throw new Error(`Duplicate MoScript ID detected: "${script.id}"`);
            }
            seen.add(script.id);
        }
        return true;
    }
}
