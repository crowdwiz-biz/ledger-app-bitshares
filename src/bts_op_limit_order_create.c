/*******************************************************************************
*  Copyright of the Contributing Authors, including:
*
*   (c) 2019 Christopher J. Sanborn
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
********************************************************************************/

#include "bts_op_limit_order_create.h"
#include "bts_types.h"
#include "os.h"

uint32_t deserializeBtsOperationLimitOrderCreate(const uint8_t *buffer, uint32_t bufferLength, bts_operation_limit_order_create_t * op) {

    uint32_t read = 0;
    uint32_t gobbled = 0;

    gobbled = deserializeBtsAssetType(buffer, bufferLength, &op->feeAsset);
    if (gobbled > bufferLength) {
        THROW(EXCEPTION);
    }
    read += gobbled; buffer += gobbled; bufferLength -= gobbled;

    gobbled = deserializeBtsAccountIdType(buffer, bufferLength, &op->sellerId);
    if (gobbled > bufferLength) {
        THROW(EXCEPTION);
    }
    read += gobbled; buffer += gobbled; bufferLength -= gobbled;

    gobbled = deserializeBtsAssetType(buffer, bufferLength, &op->sellAsset);
    if (gobbled > bufferLength) {
        THROW(EXCEPTION);
    }
    read += gobbled; buffer += gobbled; bufferLength -= gobbled;

    gobbled = deserializeBtsAssetType(buffer, bufferLength, &op->buyAsset);
    if (gobbled > bufferLength) {
        THROW(EXCEPTION);
    }
    read += gobbled; buffer += gobbled; bufferLength -= gobbled;

    gobbled = deserializeBtsTimeType(buffer, bufferLength, &op->expires);
    if (gobbled > bufferLength) {
        THROW(EXCEPTION);
    }
    read += gobbled; buffer += gobbled; bufferLength -= gobbled;

    gobbled = deserializeBtsBoolType(buffer, bufferLength, &op->fillOrKill);
    if (gobbled > bufferLength) {
        THROW(EXCEPTION);
    }
    read += gobbled; buffer += gobbled; bufferLength -= gobbled;

    gobbled = deserializeBtsExtensionArrayType(buffer, bufferLength, &op->extensions);
    if (gobbled > bufferLength) {
        THROW(EXCEPTION);
    }
    read += gobbled; buffer += gobbled; bufferLength -= gobbled;

    if (op->extensions.count > 0) {
      op->containsUninterpretable = true;
    } else {
      op->containsUninterpretable = false;
    }

    PRINTF("DESERIAL: OP_LIMIT_CREATE: Read %d bytes; Buffer remaining: %d bytes\n", read, bufferLength);

    return read;

}
