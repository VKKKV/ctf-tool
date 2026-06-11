package ttd

import (
  "encoding/hex"
)

type Level04 struct {
  LevelBase
}

func (level Level04) Run() {
  data := "0C02D8010D0C02D8010606D8101402FCD80F0603D8FC0600DA"

  dataHex, err := hex.DecodeString(data)
  if err != nil {
    level.logger.Fatalln(err)
  }

  var solution []byte
  var i int
  for _, c := range dataHex {
    if c >= 0 && c <= 30 {
      i = int(30 - c)
    } else {
      i = int(255 - c) + 31
    }

    solution = append(solution, Alphabet[i % len(Alphabet)])
  }

  level.logger.Println(string(solution))
  level.solve(solution)
}
