/** 搜索算法 **/

// 计算两个字符串的Levenshtein距离 [莱文斯坦距离]
function levenshteinDistance(str1, str2) {
    const matrix = [];
    const len1 = str1.length;
    const len2 = str2.length;
    // 初始化矩阵
    for (let i = 0; i <= len1; i++) {
        matrix[i] = [i];
    }
    for (let j = 0; j <= len2; j++) {
        matrix[0][j] = j;
    }
    // 计算距离
    for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
            if (str1.charAt(i - 1) === str2.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1, // 替换
                    matrix[i][j - 1] + 1,     // 插入
                    matrix[i - 1][j] + 1      // 删除
                );
            }
        }
    }
    return matrix[len1][len2];
}

// 计算相似度 (0-1) 
function similarity(str1, str2) {
    const distance = levenshteinDistance(str1.toLowerCase(), str2.toLowerCase());
    const maxLength = Math.max(str1.length, str2.length);
    return maxLength === 0 ? 1 : 1 - (distance / maxLength);
}

/**
 * 查找与输入字符串相似的列表元素
 * @param {string} input - 输入的字符串
 * @param {string[]} list - 字符串列表
 * @param {number} threshold - 相似度阈值 (0-1)，默认0.5
 * @returns {string[]} - 匹配的相似字符串列表
 */
function findSimilarStrings(input, list, threshold = 0.5) {
    // 过滤相似度超过阈值的字符串
    return list.filter(item => similarity(input, item) >= threshold)
        .sort((a, b) => similarity(input, b) - similarity(input, a));
}

export { levenshteinDistance, similarity, findSimilarStrings }

