function addr_short(address) {
  if (address == 0) return '';
  //return address.substring(0,6)+'..'+address.slice(-2);
  return address.substring(0,9)+'..';
}

function formatq(n, div) {
  if (div != 0 && div != 1) return '#DivisibilityUnknown';
  if (n == '0') return 'zero';
  //Divisible tokens shall always have 8 decimals
  //Indivisble tokens shall have no decimals
  //Integral part shall use digit grouping if >9999
  let plural_s = (n == 1 && div == 0 || n == 100000000 && div == 1) ? '' : 's';
  n = String(n);
  let decimal = '';
  let integral = ''
  if (div == 1) {
    n = n.padStart(9, '0');
    decimal = n.slice(-8);
    decimal = '<span style="color: dimgray">.' + decimal + '</span>';
    integral = n.slice(0,-8);
  } else {
    integral = n;
  }
  if (integral.length >= 5) {
    integral = integral.replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,")        
  }
  if (div == 1) return integral + decimal + ' token' + plural_s;
  return integral + ' token' + plural_s;
}

function mark_keyword(str, key) {
  key = key.toUpperCase();
  str_uc = str.toUpperCase();
  key_uc = key.toUpperCase();

  let ind = str_uc.indexOf(key_uc);
  let len = key.length;

  if (ind == -1) {
    //try key with a space
    for (let i = 1; i < len; i++) {
      let key_space = [key.slice(0, i), ' ', key.slice(i)].join('');
      //console.log(key_space);
      ind = str_uc.indexOf(key_space);
      if (ind > -1) {
        len += 1;
        break;
      }
    }
  }

  if (ind == -1) {
    //latinize foreign characters
    let str_l = latinize(str).toUpperCase();
    ind = str_l.indexOf(key_uc);
    if (ind == -1) return str; //keyword not found
    //Find pos of key equivialent in original alphabet
    let key_l = latinize(key_uc);
    loop1: for (let i = Math.floor(len/2); i <= Math.ceil(len*2); i++) {
      for (let j = 0; j < str_uc.length; j++) {
        let trykey = str.slice(j, j+i);
        if (key_l == latinize(trykey).toUpperCase()) {
          console.log(trykey);
          ind = j;
          len = i;
          break loop1;
        }
      }
    }
  } 

  return str.slice(0, ind) + '<mark style="background-color:#FFFF66">' + str.slice(ind, ind+len) + '</mark>' + str.slice(ind+len);

}

function search_color() {
  let val = document.getElementById('search').value;
  if (val.includes('.')) {
    //subasset
  } else {
    val = val.toUpperCase();
  }
  if (assets.includes(val)) {
    document.getElementById('search').style.backgroundColor = 'palegreen';
  } else {
    document.getElementById('search').style.backgroundColor = 'white';
  }
}


function isValidAsset(asset) {
  if (isValidAlphabeticAsset(asset) || isValidNumericAsset(asset) || isValidSubasset(asset)) return true;
  return false;
}

function isValidAlphabeticAsset(asset) {
  //4-12 chars, cannot start with A
  //A few old ones have 13 or 14 chars
  if (/^[B-Z][A-Z]{3,11}$/.test(asset) == false) return false;
  return true;
}

function isValidNumericAsset(asset) {
  //'A' followed by a really large number
  //Min = 26^12+1 =    95,428,956,661,682,177
  //Max = 2^64-1 = 18,446,744,073,709,551,615
  if (asset.length>21) return false;
  if (asset.length<18) return false;
  if (asset[0] != 'A') return false;
  if (asset.substring(0,2) == 'A0') return false;
  if (/^[0-9]*$/.test(asset.substring(1)) == false) return false;
  if (asset.length==18 && asset.substring(1,9)<95428956) return false;
  if (asset.length==18 && asset.substring(1,9)==95428956  && asset.substring(9)<661682177) return false;
  if (asset.length==21 && asset.substring(1,10)>184467440) return false;
  if (asset.length==21 && asset.substring(1,10)==184467440  && asset.substring(10)>73709551615) return false;
  return true;
}

function isValidSubasset(asset) {
  /*Subasset names must meet following requirements :
          1. Begin with the parent asset name followed by a period (.)
          2. Contain at least 1 character following the parent asset name and a period (.) (e.g. PIZZA.x)
          3. Contain up to 250 characters in length including the parent asset name (e.g. PIZZA.REALLY-long-VALID-Subasset-NAME)
          4. Contain only characters a-zA-Z0-9.-_@!
          5. Cannot end with a period (.)
          6. Cannot contain multiple consecutive periods (..)*/

  let parent = asset.split('.')[0];
  let sub = asset.replace(parent+'.', '');

  if (isValidAlphabeticAsset(parent) == false) return false;
  if (asset.includes('.') == false) return false;
  if (sub.length < 1) return false;
  if (asset.length > 250) return false;
  if (/^[a-zA-Z0-9\.\-_@!]*$/.test(sub) == false) return false;
  if (sub.slice(-1) == '.') return false;
  if (asset.includes('..')) return false;
  return true;
}

function isMatch(searchOnString, searchText) {
  searchText = searchText.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  return searchOnString.match(new RegExp("\\b"+searchText+"\\b", "i")) != null;
}