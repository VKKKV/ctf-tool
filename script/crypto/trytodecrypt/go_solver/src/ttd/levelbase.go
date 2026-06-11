package ttd

import (
  "errors"
  "strconv"
  "log"
)

const (
  Alphabet = "0123456789" +
  "abcdefghijklmnopqrstuvwxyz" +
  "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
  "-_.,;:?! "
)

type LevelBase struct {
  id int
  api TTD
  logger *log.Logger
}

type LevelInterface interface {
  Run()
}

func NewLevel(id int, api TTD, logger *log.Logger) (LevelInterface, error) {
  switch id {
    case 1: return Level01{LevelBase{id, api, logger}}, nil
    case 2: return Level02{LevelBase{id, api, logger}}, nil
    case 3: return Level03{LevelBase{id, api, logger}}, nil
    case 4: return Level04{LevelBase{id, api, logger}}, nil
    case 5: return Level05{LevelBase{id, api, logger}}, nil
    case 6: return Level06{LevelBase{id, api, logger}}, nil
    default: return nil, errors.New("Level " + strconv.Itoa(id) + " is not implemented")
  }
}

func (level *LevelBase) solve(solution []byte) {
  solved, err := level.api.Solve(level.id, []byte(solution))
  if err != nil {
    level.logger.Fatalln(err)
  }

  if solved {
    level.logger.Println("OK")
  } else {
    level.logger.Fatalln("Fail")
  }
}
