import { all, fork } from "redux-saga/effects"
import { overviewSaga } from "./overviewSaga"
import { usersSaga } from "./usersSaga"

export function* rootSaga() {
  yield all([fork(overviewSaga), fork(usersSaga)])
}
