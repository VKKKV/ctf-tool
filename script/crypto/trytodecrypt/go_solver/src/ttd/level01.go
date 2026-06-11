package ttd

import (
  "encoding/hex"
)

type Level01 struct {
  LevelBase
}

func (level Level01) Run() {
  data := "131017171A48221A1D170F"

  dataHex, err := hex.DecodeString(data)
  if err != nil {
    level.logger.Fatalln(err)
  }

  var solution []byte
  for _, c := range dataHex {
    solution = append(solution, Alphabet[int(c - 2)])
  }

  level.logger.Println(string(solution))
  level.solve(solution)
}
