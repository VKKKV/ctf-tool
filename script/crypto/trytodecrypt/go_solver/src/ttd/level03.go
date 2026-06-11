package ttd

import (
  "encoding/hex"
)

type Level03 struct {
  LevelBase
}

func (level Level03) Run() {
  data := "0A0B1339150B1139070A0B13390510"

  dataHex, err := hex.DecodeString(data)
  if err != nil {
    level.logger.Fatalln(err)
  }

  var solution []byte
  for _, c := range dataHex {
    solution = append(solution, Alphabet[int(c + 13)])
  }

  level.logger.Println(string(solution))
  level.solve(solution)
}
