package ttd

import (
  "encoding/hex"
)

type Level06 struct {
  LevelBase
}

func (level Level06) Run() {
  data := "4D586CFC2DB449D47B0CF99C3BC46CFC7B0C"
  dataHex, err := hex.DecodeString(data)
  if err != nil {
    level.logger.Fatalln(err)
  }

  alphabet := level.genAlphabet()
  var solution []rune
  for i := 0; i < len(dataHex); i += 2 {
    k := [2]byte{
      dataHex[i],
      dataHex[i + 1],
    }
    solution = append(solution, alphabet[k])
  }

  level.logger.Println(string(solution))
  level.solve([]byte(string(solution)))
}

func (level Level06) genAlphabet() map[[2]byte]rune {
  alphabet := make(map[[2]byte]rune, 0)
  var j byte
  var i byte = 3
  var j1 byte = 132
  var j2 byte = 8
  for b, c := range Alphabet {
    if b % 2 == 0 {
      j = j1
    } else {
      j = j2
    }

    alphabet[[2]byte{i, j}] = c
    if b % 2 == 0 {
      j1 += 8
    } else {
      j2 += 8
    }

    if b >= len(Alphabet) / 2 - 4 {
      b %= len(Alphabet) / 2 - 4
    }

    if b % 2 == 0 {
      i += 4
    } else {
      i += 3
    }
  }

  return alphabet
}
