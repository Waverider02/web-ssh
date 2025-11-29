import { toRaw } from "vue";

// 实现A,B中相同属性赋值,输出为B
function assignSame(A, B) {
    Object.keys(B).forEach(k => k in A && (B[k] = A[k]));
    return toRaw(B);
}

// 清空对象中数据
function clearItem(A) {
    Object.keys(A).forEach(k => {
        const t = typeof A[k];
        if (t === 'string') A[k] = '';
        else if (t === 'boolean') A[k] = false;
        else if (t === 'number') A[k] = 0;
    });
}

/**
 * 返回 A 与 B 的并集（按第一次出现的顺序，已去重）
 * @param {Array} A
 * @param {Array} B
 * @returns {Array} 并集
 */
function union(A, B) {
    const set = new Set();      // 用来去重
    return [...A, ...B].filter(x => {
        if (set.has(x)) return false;
        set.add(x);
        return true;
    });
}


export { assignSame, clearItem, union }