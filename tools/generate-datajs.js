const fs = require('fs');
const path = require('path');

function readText(filePath) {
  return fs.readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '');
}

function safeJsonParse(raw, fallback) {
  try {
    return JSON.parse(raw);
  } catch (e) {
    return fallback;
  }
}

function parseJsonListFromPublicJs(content) {
  const items = [];
  const re =
    /\{\s*id:\s*"([^"]+)"\s*,\s*name:\s*'([^']*)'\s*,\s*describe:\s*'([^']*)'\s*,\s*file:\s*"([^"]+)"\s*\}/g;
  let m = null;
  while ((m = re.exec(content)) !== null) {
    items.push({
      id: m[1],
      name: m[2],
      describe: m[3],
      file: m[4]
    });
  }
  return items;
}

function jsStringify(value) {
  return JSON.stringify(value, null, 2);
}

const projectRoot = path.join(__dirname, '..');
const jsonDir = path.join(projectRoot, 'json');
const publicJsPath = path.join(projectRoot, 'js', 'public.js');
const outPath = path.join(projectRoot, 'js', 'data.js');

const publicJs = readText(publicJsPath);
const banks = parseJsonListFromPublicJs(publicJs).map((b) => ({
  id: b.id,
  name: b.name,
  describe: b.describe,
  file: b.id,
  source: 'builtIn'
}));

const builtInData = {};
banks.forEach((b) => {
  const jsonFilePath = path.join(jsonDir, `${b.id}.json`);
  if (!fs.existsSync(jsonFilePath)) {
    throw new Error(`缺少题库文件：${jsonFilePath}`);
  }
  const list = safeJsonParse(readText(jsonFilePath), []);
  if (!Array.isArray(list)) {
    throw new Error(`题库文件格式不正确：${jsonFilePath}`);
  }
  builtInData[b.id] = list;
});

const content = `(function () {
  function safeParse(raw, fallback) {
    try {
      var v = JSON.parse(raw || '');
      return v && typeof v === 'object' ? v : fallback;
    } catch (e) {
      return fallback;
    }
  }

  var builtInBanks = ${jsStringify(banks)};
  var builtInData = ${jsStringify(builtInData)};

  var extraStore = safeParse(localStorage.getItem('datajs_extra_store'), { banks: [], data: {} });
  var extraBanks = Array.isArray(extraStore.banks) ? extraStore.banks : [];
  var extraData = extraStore.data && typeof extraStore.data === 'object' ? extraStore.data : {};

  var bankMap = {};
  builtInBanks.forEach(function (b) {
    bankMap[b.id] = b;
  });
  extraBanks.forEach(function (b) {
    if (b && b.id && !bankMap[b.id]) {
      bankMap[b.id] = b;
    }
  });

  var mergedBanks = Object.keys(bankMap).map(function (k) {
    return bankMap[k];
  });

  var mergedData = {};
  Object.keys(builtInData).forEach(function (k) {
    mergedData[k] = builtInData[k];
  });
  Object.keys(extraData).forEach(function (k) {
    if (!mergedData[k]) {
      mergedData[k] = extraData[k];
    }
  });

  window.BankList = mergedBanks;
  window.QuestionData = mergedData;
})();`;

fs.writeFileSync(outPath, content, 'utf8');
console.log(`已生成：${outPath}`);

