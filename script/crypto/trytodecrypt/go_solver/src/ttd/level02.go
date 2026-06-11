package ttd

import (
  "encoding/hex"
)

type Level02 struct {
  LevelBase
}

func (level Level02) Run() {
  data := "4A3E374A4973483F3D3E4A"

  dataHex, err := hex.DecodeString(data)
  if err != nil {
    level.logger.Fatalln(err)
  }

  var solution []byte
  for _, c := range dataHex {
    solution = append(solution, Alphabet[int(c - 45)])
  }

  level.logger.Println(string(solution))
  level.solve(solution)
}
