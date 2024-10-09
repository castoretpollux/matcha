export function isEmpty(obj) {
    if (obj) {
        return Object.keys(obj).length === 0;
    } else {
        return true
    }
}

export function getUrlType(url) {
    // Extraire l'extension de fichier de l'URL
    const extension = url.split('.').pop().toLowerCase();

    // Comparer l'extension avec les extensions courantes pour les images, les PDF et les fichiers DOCX
    if (extension === 'jpg' || extension === 'jpeg' || extension === 'png' || extension === 'gif' || extension === 'svg') {
        return 'image';
    } else if (extension === 'pdf') {
        return 'pdf';
    } else {
        return 'doc';
    }
}

export function setNodeError(node) {
    node.classList.add('error');
    if (node.nextElementSibling) {
        node.nextElementSibling.style.display = 'block';
    }
}

// Function to validate an input element and manage error display
export function validateTrimInput(inputValue, inputNode) {
    if (inputValue.trim()) {
        return true;
    } else {
        setNodeError(inputNode);
        return false;
    }
}

export function checkRequiredFields(schema, dataToSend) {
    const requiredDatas = getRequiredFields(schema);

    let not_required = true;

    for (const [key, value] of Object.entries(dataToSend)) {
        if (!not_required) break;

        if (isFieldRequired(requiredDatas, key, value) || isFieldDependentRequired(schema, dataToSend, key, value)) {
            not_required = false;
            break;
        }
    }

    return not_required;
}

function getRequiredFields(schema) {
    const requiredDatas = {};
    for (const item in schema['properties']) {
        requiredDatas[item] = schema.properties[item].extra?.required;
    }
    return requiredDatas;
}

function isValueEmpty(value) {
    if (typeof value === 'string') {
        return value.trim().length === 0;
    }
    return value == null || value == undefined;
}

function isFieldRequired(requiredDatas, key, value) {
    const value_is_required = requiredDatas[key];
    return value_is_required && isValueEmpty(value);
}

function isFieldDependentRequired(schema, dataToSend, key, value) {
    const required_if = schema.properties[key]?.extra?.required_if;
    if (!required_if) return false;

    for (const [required_key, required_value] of Object.entries(required_if)) {
        let dataValue = dataToSend[required_key];
        if (isValueEmpty(dataValue)) {
            dataValue = null;
        }

        if (required_value == dataValue && isValueEmpty(value)) {
            return true;
        }
    }

    return false;
}


export function getBounds(element) {
    return {
        x: element.offsetLeft,
        y: element.offsetTop,
        w: element.offsetWidth,
        h: element.offsetHeight,
    }
}

export function formatValue(value) {
    if (value === 'on') return true
    if (value === 'off') return false
    if (value === undefined || value === null) return null
    return value
}

export function deepEqualObj(obj1, obj2) {
    if (obj1 === obj2) return true;

    if (typeof obj1 !== 'object' || obj1 === null || typeof obj2 !== 'object' || obj2 === null) {
        return false;
    }

    let keys1 = Object.keys(obj1);
    let keys2 = Object.keys(obj2);

    if (keys1.length !== keys2.length) {
        return false;
    }

    for (let key of keys1) {
        if (!keys2.includes(key) || !deepEqualObj(obj1[key], obj2[key])) {
            return false;
        }
    }

    return true;
}

export function deepEqualArray(arr1, arr2) {
    if (arr1 === arr2) return true;

    if (!Array.isArray(arr1) || !Array.isArray(arr2) || arr1.length !== arr2.length) {
        return false;
    }

    for (let i = 0; i < arr1.length; i++) {
        if (!deepEqualObj(arr1[i], arr2[i])) {
            return false;
        }
    }

    return true;
}