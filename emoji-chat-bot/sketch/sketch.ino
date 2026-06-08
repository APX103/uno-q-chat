#include "Arduino_LED_Matrix.h"
#include "Arduino_RouterBridge.h"

ArduinoLEDMatrix matrix;

uint8_t frame[104];

void clear_frame() {
  memset(frame, 0, sizeof(frame));
}

void show_expression(const uint8_t* expr) {
  memcpy(frame, expr, 104);
  matrix.draw(frame);
}

// 表情（8×13，用户最新设计）

const uint8_t EXPR_UNKNOWN[104] = {
  0,0,0,0,1,1,1,1,1,0,0,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,1,0,0,1,0,1,0,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,1,0,1,1,1,1,1,0,1,0,0,
  0,0,1,0,1,0,0,0,1,0,1,0,0,
  0,0,1,0,0,1,1,1,0,0,1,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0
};

// 好
const uint8_t EXPR_GOOD[104] = {
  0,0,0,0,1,1,1,1,1,0,0,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,1,0,0,1,0,1,0,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,1,0,1,0,0,0,1,0,1,0,0,
  0,0,1,0,0,1,1,1,0,0,1,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,0,0,1,1,1,1,1,0,0,0,0
};

// 一般
const uint8_t EXPR_AVERAGE[104] = {
  0,0,0,0,1,1,1,1,1,0,0,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,1,0,0,1,0,1,0,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,1,0,1,1,1,1,1,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,0,0,1,1,1,1,1,0,0,0,0
};

// 差
const uint8_t EXPR_BAD[104] = {
  0,0,0,0,1,1,1,1,1,0,0,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,1,0,0,1,0,1,0,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,1,0,0,1,1,1,0,0,1,0,0,
  0,0,1,0,1,0,0,0,1,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,0,1,1,1,1,1,1,1,0,0,0
};

// 难受
const uint8_t EXPR_UNCOMFORTABLE[104] = {
  0,0,0,0,1,1,1,1,1,0,0,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,1,0,0,1,0,1,0,0,1,0,0,
  0,0,1,0,1,1,0,1,1,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,1,0,0,1,1,1,0,0,1,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,0,0,1,1,1,1,1,0,0,0,0
};

// 酷
const uint8_t EXPR_COOL[104] = {
  0,0,0,0,1,1,1,1,1,0,0,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,1,1,1,1,1,1,1,1,1,0,0,
  0,0,1,0,1,1,0,1,1,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,1,0,0,1,1,1,0,0,1,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,0,0,1,1,1,1,1,0,0,0,0
};

// danger 复用"酷"
const uint8_t EXPR_DANGER[104] = {
  0,0,0,0,1,1,1,1,1,0,0,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,1,1,1,1,1,1,1,1,1,0,0,
  0,0,1,0,1,1,0,1,1,0,1,0,0,
  0,0,1,0,0,0,0,0,0,0,1,0,0,
  0,0,1,0,0,1,1,1,0,0,1,0,0,
  0,0,0,1,0,0,0,0,0,1,0,0,0,
  0,0,0,0,1,1,1,1,1,0,0,0,0
};

String set_expression(String expr_name) {
  clear_frame();

  if (expr_name == "good") {
    show_expression(EXPR_GOOD);
  } else if (expr_name == "average") {
    show_expression(EXPR_AVERAGE);
  } else if (expr_name == "uncomfortable") {
    show_expression(EXPR_UNCOMFORTABLE);
  } else if (expr_name == "bad") {
    show_expression(EXPR_BAD);
  } else if (expr_name == "cool") {
    show_expression(EXPR_COOL);
  } else if (expr_name == "danger") {
    show_expression(EXPR_DANGER);
  } else if (expr_name == "unknown") {
    show_expression(EXPR_UNKNOWN);
  } else {
    show_expression(EXPR_UNKNOWN);
    return "ERROR: unknown '" + expr_name + "', showing unknown";
  }

  Monitor.println("Expression: " + expr_name);
  return "OK";
}

void setup() {
  Bridge.begin();
  Monitor.begin();

  matrix.begin();
  matrix.setGrayscaleBits(1);

  Bridge.provide_safe("set_expression", set_expression);

  show_expression(EXPR_UNKNOWN);
  Monitor.println("LED Matrix Bridge ready");
}

void loop() {
  delay(10);
}
