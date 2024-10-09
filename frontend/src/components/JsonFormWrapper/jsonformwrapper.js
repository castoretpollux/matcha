import { formatValue } from "../../helpers/utils"

export function getInitialData(dataSchema) {
    const data = {}
    for (let item in dataSchema['properties']) {
        // Check in base default
        let defaultValue = dataSchema.properties[item].default
        if (!defaultValue) {
            // Check in extra default (UI Fields)
            defaultValue = dataSchema.properties[item].extra?.default
        }

        if (defaultValue === null || defaultValue === undefined) {
            if (dataSchema.properties[item].type == 'string') {
                defaultValue = ''
            } else if (dataSchema.properties[item].type == 'boolean') {
                defaultValue = false
            }
        }
        data[item] = defaultValue
    }
    return data
}

export function checkRequiredFields(properties, dataToSend) {
    for (const [key, value] of Object.entries(dataToSend)) {
        const required = properties[key]?.required
        if (required && !formatValue(value)) {
            return false
        }
    }
    return true
}

export function getSchemaProperties(schema) {
    // Get required fields
    const properties = {}

    for (const item in schema['properties']) {
        properties[item] = {}
        properties[item]['required'] = schema.properties[item].extra?.required
        // Add another properties here
    }

    return properties
}


export function getSchemaRules(uischema) {
    const rules = {}
    for (let row of uischema.elements) {
        for (let field of row.elements) {
            if (field.options?.rule) rules[field.scope] = field.options?.rule
        }
    }
    return rules
}


export function checkSchemaRules(schemaRules, schemaProperties, dataToSend, parentNodeId) {
    for (const field of Object.keys(dataToSend)) {
        const scope = `#/properties/${field}`;
        const rules = schemaRules[scope];
        if (rules) {
            rules.forEach((rule) => {
                let operand = 'AND'
                if (rule.condition.operand) {
                    operand = rule.condition.operand
                    delete rule.condition.operand
                }

                const conditions = []

                for (const [key, data] of Object.entries(rule.condition)) {
                    const operatorFunction = operators[data.kind]
                    const valueToTest = formatValue(dataToSend[key])
                    conditions.push(operatorFunction(valueToTest, data.value))
                }

                const operandFunction = operands[operand]
                const condition = operandFunction(...conditions)

                if (rule.action.css) {
                    for (const [effect, state] of Object.entries(rule.action.css)) {

                        let value = state
                        if (!condition) value = !value;

                        useEffect(parentNodeId, scope, effect, value)
                    }
                }

                if (rule.action.property) {
                    for (const [effect, propertyValue] of Object.entries(rule.action.property)) {
                        const value = formatPropertyValue(propertyValue, condition, dataToSend)
                        schemaProperties[field][effect] = value
                        useProperty(parentNodeId, scope, effect, value)
                    }
                }

                if (rule.action.value && condition) {
                    for (const [, targetValue] of Object.entries(rule.action.value)) {
                        const value = formatValue(targetValue)
                        useValue(parentNodeId, scope, typeofValue(value), value)
                        dataToSend[field] = value
                    }
                }

            })
        }
    }
    return [schemaProperties, dataToSend]
}

const useEffect = (parentNodeId, scope, effect, value) => {
    const parentNode = document.getElementById(parentNodeId)
    const node = parentNode.querySelector(`[id="wrapper-${scope}"]`)

    if (value) node?.classList.add(effect)
    else node?.classList.remove(effect)
}

const useProperty = (parentNodeId, scope, effect, value) => {
    const parentNode = document.getElementById(parentNodeId)
    const node = parentNode.querySelector(`[id="${scope}"]`)

    if (value) node?.setAttribute(effect, value)
    else node?.removeAttribute(effect)
}

const useValue = (parentNodeId, scope, type, value) => {
    const parentNode = document.getElementById(parentNodeId)
    const node = parentNode.querySelector(`[id="${scope}"]`)
    if (type === 'boolean') node.checked = value
    else node.value = value
}

const formatPropertyValue = (value, condition, dataToSend) => {
    if (typeof value == 'boolean') {
        if (!condition) value = !value;
        return value
    } else if (typeof value == 'string') {
        let valueToSend = value
        const matches = value.match(/<([^>]+)>/g); // NOSONAR
        if (matches) {
            const keys = matches.map(match => match.replace(/[<>]/g, ""));
            for (const targetKey of keys) {
                const newValue = formatValue(dataToSend[targetKey])
                valueToSend = valueToSend.replace(`<${targetKey}>`, newValue)
            }
        }
        return valueToSend
    }
    return value
}


const operators = {
    'exact': (a, b) => a === b,
    'in': (a, b) => b.includes(a),
    'not': (a, b) => a != b,
  };

const operands = {
    'AND': (...args) => args.reduce((acc, val) => acc && val, true),
    'OR': (...args) => args.reduce((acc, val) => acc || val, true),
}

const typeofValue = (value) => {
    if (typeof value === 'boolean' | value == 'on' | value == 'off') return 'boolean'
    else return typeof value
}