package ttd

import (
  "encoding/hex"
)

type Level05 struct {
  LevelBase
}

func (level Level05) Run() {
  data := "90DE633F425148DE51546CDE725466DE3F2A6936DE4263CCDEAB362A3372DE39545DDE633F36DE51366F63DE545136D8"

  dataHex, err := hex.DecodeString(data)
  if err != nil {
    level.logger.Fatalln(err)
  }

  var solution []byte
  for _, c := range dataHex {
    b := int(c - 12)
    solution = append(solution, Alphabet[b / 3])
  }

  level.logger.Println(string(solution))
  level.solve(solution)
}
